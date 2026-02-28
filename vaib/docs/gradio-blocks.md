# Gradio Blocks Documentation

## Blocks

```
gr.Blocks()
```

### Description

Blocks is Gradio's low-level API that allows you to create more custom web applications and demos than Interfaces (yet still entirely in Python). Compared to the Interface class, Blocks offers more flexibility and control over: (1) the layout of components (2) the events that trigger the execution of functions (3) data flows (e.g. inputs can trigger outputs, which can trigger the next level of outputs). Blocks also offers ways to group together related demos such as with tabs.

### Example Usage

```python
import gradio as gr

def update(name):
    return f"Welcome to Gradio, {name}!"

with gr.Blocks() as demo:
    gr.Markdown("Start typing below and then click **Run** to see the output.")
    with gr.Row():
        name = gr.Textbox(label="What is your name?")
        output = gr.Textbox(label="Output")
    btn = gr.Button("Run")
    btn.click(update, name, output)

demo.launch()
```

### Initialization Parameters

- `analytics_enabled: bool | None` - allow basic telemetry
- `mode: str` - human-friendly name for Blocks type (default: "blocks")
- `title: str | I18nData` - tab title (default: "Gradio")
- `fill_height: bool` - vertically expand to window height (default: False)
- `fill_width: bool` - horizontally expand to fill container (default: False)
- `delete_cache: tuple[int, int] | None` - cache deletion frequency and age

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
