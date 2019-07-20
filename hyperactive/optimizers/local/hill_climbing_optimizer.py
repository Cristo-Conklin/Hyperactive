# Author: Simon Blanke
# Email: simon.blanke@yahoo.com
# License: MIT License


from ...base import BaseOptimizer
from ...base import BasePositioner


class HillClimbingOptimizer(BaseOptimizer):
    def __init__(
        self,
        search_config,
        n_iter,
        metric="accuracy",
        n_jobs=1,
        cv=5,
        verbosity=1,
        random_state=None,
        warm_start=False,
        memory=True,
        scatter_init=False,
        eps=1,
    ):
        super().__init__(
            search_config,
            n_iter,
            metric,
            n_jobs,
            cv,
            verbosity,
            random_state,
            warm_start,
            memory,
            scatter_init,
        )

        self.eps = eps
        self.initializer = self._init_climber

    def _iterate(self, i, _cand_, X, y):
        self._climber_.climb(_cand_)
        _cand_.pos = self._climber_.pos
        _cand_.eval(X, y)

        if _cand_.score > _cand_.score_best:
            _cand_.score_best = _cand_.score
            _cand_.pos_best = _cand_.pos

        return _cand_

    def _init_climber(self, _cand_):
        self._climber_ = HillClimber(self.eps)


class HillClimber(BasePositioner):
    def __init__(self, eps):
        self.eps = eps
