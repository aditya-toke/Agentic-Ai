# agent/feedback.py
# Experience-based learning from admin decisions

class FeedbackLearner:
    def __init__(self):
        # memory structure:
        # {
        #   error_type: {
        #       action_name: {"success": int, "fail": int}
        #   }
        # }
        self.memory = {}

    def record(self, error_type, action, approved):
        if error_type not in self.memory:
            self.memory[error_type] = {}

        if action not in self.memory[error_type]:
            self.memory[error_type][action] = {"success": 0, "fail": 0}

        if approved:
            self.memory[error_type][action]["success"] += 1
        else:
            self.memory[error_type][action]["fail"] += 1

    def best_action(self, error_type):
        if error_type not in self.memory:
            return None

        best = None
        best_score = -1

        for action, stats in self.memory[error_type].items():
            total = stats["success"] + stats["fail"]
            if total == 0:
                continue

            score = stats["success"] / total
            if score > best_score:
                best_score = score
                best = action

        return best

    def get_stats(self):
        return self.memory


# Global shared memory
feedback_learner = FeedbackLearner()
