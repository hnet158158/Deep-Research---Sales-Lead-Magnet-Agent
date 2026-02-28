# Gradio Interface Documentation

## Interface

```
gr.Interface()
```

### Description

Interface is Gradio's main high-level class, and allows you to create a web-based GUI / demo around a machine learning model (or any Python function) in a few lines of code. You must specify three parameters: (1) the function to create a GUI for (2) the desired input components and (3) the desired output components. Additional parameters can be used to control the appearance and behavior of the demo.

### Example Usage

```python
import gradio as gr

def image_classifier(image):
    return {'cat': 0.3, 'dog': 0.7}

demo = gr.Interface(
    fn=image_classifier,
    inputs="image",
    outputs="label"
)
demo.launch()
```

### Initialization Parameters

- `fn: Callable` - the function to wrap an interface around
- `inputs: str | Component | list[str | Component] | None` - input components
- `outputs: str | Component | list[str | Component] | None` - output components
- `examples: list[dict] | list[list] | str | None` - sample inputs
- `cache_examples: bool | None` - cache examples for fast runtime
- `cache_mode: ['eager', 'lazy'] | None` - caching mode
- `examples_per_page: int` - how many examples to display per page (default: 10)
- `example_labels: list[str] | None` - labels for each example
- `preload_example: int | False` - preload example at index
- `live: bool` - automatically rerun if inputs change (default: False)
- `title: str | I18nData | None` - title for the interface
- `description: str | None` - description for the interface
- `article: str | None` - expanded article explaining the interface
- `flagging_mode: ['never', 'auto', 'manual'] | None` - flagging mode
- `flagging_options: list[str] | list[tuple[str, str]] | None` - flagging options
- `flagging_dir: str` - path to flagged data directory (default: ".gradio/flagged")
- `flagging_callback: FlaggingCallback | None` - callback when sample is flagged
- `analytics_enabled: bool | None` - allow basic telemetry
- `batch: bool` - process batch of inputs (default: False)
- `max_batch_size: int` - maximum batch size (default: 4)
- `api_visibility: ['public', 'private', 'undocumented']` - API endpoint visibility (default: "public")
- `api_name: str | None` - API endpoint name
- `api_description: str | None | False` - API endpoint description
- `allow_duplication: bool` - show 'Duplicate Spaces' button (default: False)
- `concurrency_limit: int | None | 'default'` - max concurrent events (default: "default")
- `additional_inputs: str | Component | list[str | Component] | None` - additional input components
- `additional_inputs_accordion: str | Accordion | None` - accordion for additional inputs
- `submit_btn: str | Button` - submit button (default: "Submit")
- `stop_btn: str | Button` - stop button (default: "Stop")
- `clear_btn: str | Button | None` - clear button (default: "Clear")
- `delete_cache: tuple[int, int] | None` - cache deletion frequency and age
- `show_progress: ['full', 'minimal', 'hidden']` - progress animation (default: "full")
- `fill_width: bool` - horizontally expand to fill container (default: False)
- `time_limit: int | None` - stream time limit in seconds (default: 30)
- `stream_every: float` - stream chunk latency in seconds (default: 0.5)
- `deep_link: str | DeepLinkButton | bool | None` - deep link for sharing
- `validator: Callable | None` - validation function

### Methods

#### launch()

Launches a simple web server that serves the demo.

**Parameters:**
- `inline: bool | None` - display inline in iframe
- `inbrowser: bool` - auto-launch in browser (default: False)
- `share: bool | None` - create public shareable link
- `debug: bool` - block main thread (default: False)
- `max_threads: int` - max total threads (default: 40)
- `auth: [[str, str], bool] | tuple[str, str] | list[tuple[str, str]] | None` - username/password
- `auth_message: str | None` - HTML message on login page
- `prevent_thread_lock: bool` - don't block main thread (default: False)
- `show_error: bool` - display errors in alert modal (default: False)
- `server_name: str | None` - server name (default: "127.0.0.1")
- `server_port: int | None` - server port (default: 7860)
- `height: int` - iframe height in pixels (default: 500)
- `width: int | str` - iframe width (default: "100%")
- `favicon_path: str | pathlib.Path | None` - favicon file path
- `ssl_keyfile: str | None` - SSL private key file
- `ssl_certfile: str | None` - SSL certificate file
- `ssl_keyfile_password: str | None` - SSL certificate password
- `ssl_verify: bool` - verify SSL certificate (default: True)
- `quiet: bool` - suppress print statements (default: False)
- `footer_links: list['api' | 'gradio' | 'settings' | dict[str, str]] | None` - footer links
- `allowed_paths: list[str] | None` - allowed file paths
- `blocked_paths: list[str] | None` - blocked file paths
- `root_path: str | None` - application root path
- `app_kwargs: dict[str, Any] | None` - FastAPI app kwargs
- `state_session_capacity: int` - max sessions in memory (default: 10000)
- `share_server_address: str | None` - custom FRP server address
- `share_server_protocol: ['http', 'https'] | None` - share server protocol
- `share_server_tls_certificate: str | None` - TLS certificate for custom server
- `auth_dependency: [[fastapi.Depends, str | None] | None` - external auth function
- `max_file_size: str | int | None` - max upload file size
- `enable_monitoring: bool | None` - enable traffic monitoring
- `strict_cors: bool` - prevent external domain requests (default: True)
- `node_server_name: str | None` - Node.js server name
- `node_port: int | None` - Node.js server port
- `ssr_mode: bool | None` - server-side rendering mode
- `pwa: bool | None` - Progressive Web App mode
- `mcp_server: bool | None` - MCP server mode
- `i18n: I18n | None` - custom translations
- `theme: Theme | str | None` - theme
- `css: str | None` - custom CSS
- `css_paths: str | pathlib.Path | list[str | pathlib.Path] | None` - custom CSS files
- `js: str | True | None` - custom JavaScript
