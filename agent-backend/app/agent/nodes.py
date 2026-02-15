from app.utils.llm import MAIN_LLM, SUPPORTIVE_LLM

from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
import json
from app.agent.pipeline import node1_pipeline

from app.utils.clean_load_json import remove_json_prefix_list, _PARSE_FAILED

class ExtractionGenerationNode:
    def __call__(self, state):
        user_query = state.get("user_query", "")
        user_provided_locations = state.get("user_specified_locations_coords", [])

        
        if user_provided_locations:
            response = node1_pipeline(user_query=user_query, user_provided_locations=user_provided_locations)
        
        else:
            response = node1_pipeline(user_query)
        state.update(response)
        return state


class VerificationNode:

    def _is_token_limit_error(self, msg: str) -> bool:
        token_limit_indicators = [
            "maximum context length",
            "context length",
            "input size",
            "token limit",
            "maximum tokens",
            "input tokens",
            "maximum input tokens",
            "input exceeds the maximum limit",
            "input is too long",
            "input text is too long",
            "prompt is too long",
            "prompt exceeds the maximum limit",
            "input text exceeds the maximum limit",
        ]
        msg_lower = msg.lower()
        return any(indicator.lower() in msg_lower for indicator in token_limit_indicators)

    def _build_verification_prompt(self, state_json:str) -> str:
        return (
            # "You are a Verification Agent.\n"
            # "Task: Decide if the RESPONSE inside STATE is acceptable to show to the user in a UI.\n"
            # "Judge only:\n"
            # "  1) Will it help the user when rendered on UI?\n"
            # "  2) Is tone friendly?\n"
            # # "  3) Is the structure/plausible format suitable for UI use?\n"
            # "Do NOT deeply fact-check.\n"
            # "Output format: return EXACTLY one lowercase word: 'verified' or 'not verified'.\n\n"
            # "STATE (JSON):\n"
            # f"{state_json}\n"
            "You are a Verification Agent.\n"
            "Task: Decide if the chat_response inside STATE is acceptable for a UI.\n"
            "Judge only: (1) UI helpful, (2) friendly tone. Do NOT deeply fact-check.\n"
            "Return EXACTLY one line of JSON like:\n"
            '{"verdict":"verified|not_verified","fix_code":"none|repair_format|rewrite_response|tone_polish",'
            '"reasons":["short bullet..."],"fix_hint":"one actionable fix"}\n\n'
            "STATE (JSON):\n"
            f"{state_json}\n"
        )

    def __call__(self, state):
        """
        Node 2: Verify the result from Node 1, set state.verified accordingly.
        """

        print("\n\nInside the node 2")
        relevant_fields = [
            "user_query",
            "chat_response",
            "location_to_mark_on_ui",
            "budget_table"
        ]
        relevant_state = {k: state[k] for k in relevant_fields if k in state}
        state_json = json.dumps(relevant_state, ensure_ascii=False)  
        
        no_of_summary_attempt = 0
        prompt = self._build_verification_prompt(state_json)
        while(1):
            try:
                response  =  MAIN_LLM.invoke(prompt)
                # if response.content == "not verified":
                #     print("Getting unverified response in Node 2:", response.content)
                #     state['verified'] = False
                #     state['fallback_count'] += 1
                # else:
                #     print("Getting verified response in Node 2:", response.content)
                #     state['verified'] =  True
                    
                # return state

                raw = getattr(response, "content", "")
                try:
                    result = remove_json_prefix_list(raw)
                    data =  {} if (result is _PARSE_FAILED) else result
                    verdict = (data.get("verdict") or "").lower().replace(" ", "_")
                    verified = verdict == "verified"
                    state["verified"] = verified
                    state["feedback"] = "; ".join((data.get("reasons") or [] + [data.get("fix_hint") or ""])).strip()
                    state["fix_code"] = (data.get("fix_code") or "none").lower().replace(" ", "_")
                except Exception as e:
                    print("Getting error in the Node 2 LLM response parsing:", e)
                    text = (raw or "").strip().lower()
                    state["verified"] = text == "verified"
                    state["feedback"] = raw.strip()
                    state["fix_code"] = "rewrite_response" if text != "verified" else "none"

                if not state["verified"]:
                    print("Unverified in Node 2. Reasons:", state["feedback"])
                    state["fallback_count"] += 1
                return state

            
            except ChatGoogleGenerativeAIError as e:
                print("Getting Error:", e)
                msg  = str(e).lower()
                if self._is_token_limit_error(msg) and no_of_summary_attempt < 2:
                    try:
                        compact_state_json =  self.summarize_prompt_for_token_limit(prompt, msg)
                        prompt  = self._build_verification_prompt(compact_state_json)
                        no_of_summary_attempt += 1
                        continue
                    except Exception as e:
                        print("Error after summarizaton:", e)
                        state['fallback_count'] += 1
                        state['verified'] = False
                        return state
                
                else:
                    print(f"Error in Node 2(with summary attempts:{no_of_summary_attempt}):", e)
                    state['verified'] = False
                    state['fallback_count'] += 1
                    return state
            
            except Exception as e:
                print("Error in Node 2:", e)
                state['verified'] = False
                state['fallback_count'] += 1
                return state
    
    def summarize_prompt_for_token_limit(self, state_obj, err_msg:str, budget_tokens:int = 1800)->str:
        print("\n\nInside summarize_prompt_for_under_token_limit function")

        raw_state = json.dumps(state_obj, ensure_ascii=False)

        sys = (
            "You are a concise JSON compressor.\n"
            f"Goal: Reduce the following STATE so the *final prompt* fits <= {budget_tokens} tokens of input.\n"
            "Preserve ONLY information needed for verifying UI-suitability:\n"
            "  - user_query (if present)\n"
            "  - the candidate response from Node 1\n"
            "  - fields directly used by the UI (e.g, coordinates)\n"
            "  - short flags/booleans/meta that affect presentation\n"
            "Drop verbose text, reasoning traces, and non-UI intermediates. Keep just representation of long arrays.\n"
            "Return STRICTLY minified JSON (one line). No comments or extra text."
        )

        user = f"STATE:\n{raw_state}"

        # Ask SUPPORTIVE_LLM to output minified JSON ONLY
        compact = SUPPORTIVE_LLM.invoke(f"{sys}\n\n{user}")
        compact_json_str = (getattr(compact, "content", "") or "").strip()

        try:
            json.loads(compact_json_str)
            return compact_json_str
        except Exception:
            # As a fallback, keep the original state (last resort)
            return raw_state
        
    def _parse_verification_output(self, raw: str) -> tuple[bool, str]:
        try:
            data = json.loads((raw or "").strip())
            verdict = (data.get("verdict") or "").lower().replace(" ", "_")
            verified = verdict == "verified"
            reasons = data.get("reasons") or []
            fix = data.get("fix_hint") or ""
            feedback = "; ".join([*reasons, fix]) if (reasons or fix) else ""
            return verified, feedback
        except Exception:
            text = (raw or "").strip().lower()
            if text in ("verified",):
                return True, ""
            if text in ("not verified", "not_verified"):
                return False, ""
            # Fallback: guess + surface raw text to help you debug quickly
            return ("not verified" not in text and "verified" in text), raw.strip()



class QuickFixNode:
    def __call__(self, state):
        # If Node 2 didn’t suggest a specific fix, do nothing
        print("Inside node 3 for Quick fix with:\nfeedback:", state.get("feedback") or "none")
        print("\nChat response was:", state.get("chat_response", ""))
        fix = (state.get("fix_code") or "none")
        prior = state.get("chat_response", "")
        if fix == "none":
            return state

        # Minimal LLM rewrite only (no web search, no recompute)
        from app.utils.llm import MAIN_LLM
        ordered_names = [getattr(loc, "address", getattr(loc, "address", "")) 
                         for loc in state.get("location_to_mark_on_ui", [])]
        prompt = (
            "Rewrite the RESPONSE for a user-facing UI.\n"
            "Constraints: be concise, bullet points, preserve facts, keep names, include route order and budget summary if present.\n"
            f"User query: {state.get('user_query','')}\n"
            f"Ordered route: {ordered_names}\n"
            f"Budget table: {state.get('budget_table',{})}\n"
            f"Fix intent: {fix}  # (repair_format | rewrite_response | tone_polish)\n"
            f"RESPONSE:\n{prior}"
        )
        result = MAIN_LLM.invoke(prompt)
        state["chat_response"] = getattr(result, "content", str(result))
        # reset fix tag to avoid loops
        state["fix_code"] = "none"
        return state
