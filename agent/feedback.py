# agent/feedback.py
# Experience-based learning from admin decisions
# -------------------------------------------------
# This module stores admin feedback and helps
# the agent improve future recommendations.
# -------------------------------------------------

class FeedbackLearner:
    def __init__(self):
        """
        Memory structure:
        {
            error_type: {
                action_name: {
                    "success": int,
                    "fail": int
                }
            }
        }
        """
        self.memory = {}

    # -------------------------------------------------
    # Internal recorder (core logic)
    # -------------------------------------------------
    def _record_internal(self, error_type, action, approved):
        if error_type not in self.memory:
            self.memory[error_type] = {}

        if action not in self.memory[error_type]:
            self.memory[error_type][action] = {
                "success": 0,
                "fail": 0
            }

        if approved:
            self.memory[error_type][action]["success"] += 1
        else:
            self.memory[error_type][action]["fail"] += 1

    # -------------------------------------------------
    # Public API (USED BY app.py)
    # -------------------------------------------------
    def record_feedback(self, error_type, action, success):
        """
        Records admin feedback.

        Parameters:
        - error_type: str (e.g. "Missing webhook")
        - action: str (e.g. "Reconfigure webhook")
        - success: bool (True = approved, False = rejected)
        """
        self._record_internal(error_type, action, success)

    # -------------------------------------------------
    # Learning: best action for a given error
    # -------------------------------------------------
    def best_action(self, error_type):
        """
        Returns the best learned action for a given error
        based on highest success rate.
        """
        if error_type not in self.memory:
            return None

        best_action = None
        best_score = -1

        for action, stats in self.memory[error_type].items():
            total = stats["success"] + stats["fail"]
            if total == 0:
                continue

            success_rate = stats["success"] / total

            if success_rate > best_score:
                best_score = success_rate
                best_action = action

        return best_action

    # -------------------------------------------------
    # UI / Debug helper
    # -------------------------------------------------
    def get_stats(self):
        """
        Returns full feedback memory for UI display.
        """
        return self.memory


# -------------------------------------------------
# Global shared instance (IMPORT THIS)
# -------------------------------------------------
feedback_learner = FeedbackLearner()
