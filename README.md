# Kiroshi

## TODO
- [ ] Coroutines
  - [ ] Transition to `asyncio` for the main application loop
  - [ ] Use `aiohttp` for non-blocking API requests (Github, Toggl, iCal)
- [ ] Performance Optimizations
  - [ ] Implement font caching in `src/helper.py`
  - [ ] Optimize image quantization to avoid redundant processing
  - [ ] Implement partial refresh support for EPD in `EPDManager`
- [ ] Robustness & Error Handling
  - [ ] Add retry logic for network requests
  - [ ] Improve error reporting on the display when APIs fail
  - [ ] Validate configuration files using JSON schema
- [ ] Code Quality & Maintenance
  - [ ] Add comprehensive type hints throughout the project
  - [ ] Fix memory leak in `TogglPanel` (clear `debug_boxes` in `_draw`)
  - [ ] Expand test suite with more unit and integration tests
  - [ ] Ensure consistent logging across all modules
- [ ] Feature Enhancements
  - [ ] Refactor panel lifecycle management (setup/teardown)
  - [ ] Add support for more e-Paper display models
- [x] Implement Mock EPD Library
  - [x] Modify EPD lib search mechanism
- [x] Modify `main.py`
