from .start import router as start_router
from .search_candidate import router as search_candidate_router
from .handlers_admin import router as handlers_admin_router
from .handlers_for_candidates import router as handlers_for_candidates_router
from .search_candidate_by_data import router as search_candidate_by_data_router

__all__ = ["start_router", "search_candidate_router", "handlers_admin_router", "handlers_for_candidates_router", "search_candidate_by_data_router"]
