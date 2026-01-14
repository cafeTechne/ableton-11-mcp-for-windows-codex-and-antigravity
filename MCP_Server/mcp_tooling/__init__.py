# mcp_tooling package exports
from .drummer import (
    list_genres as drummer_list_genres,
    list_patterns as drummer_list_patterns,
    search_patterns as drummer_search_patterns,
    get_pattern as drummer_get_pattern,
    generate_drum_pattern,
    generate_drum_fill,
    generate_drum_section,
)

from .transitions import (
    apply_parameter_ramp,
    configure_clip_launch,
    insert_transition_scene,
    generate_micro_fill,
    apply_reverb_throw,
)

import logging
import os

# Configure unified logging
def _setup_logging():
    # Only configure if not already configured
    if not logging.getLogger().handlers:
        log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "session.log")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        # Also log to console for debugging if running interactively? 
        # Maybe not, as it interferes with stdout tools.
        
_setup_logging()
