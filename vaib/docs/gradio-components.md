# Gradio Components Documentation

## Textbox

```
gr.Textbox()
```

### Description

Creates a textarea for user to enter string input or display string output.

### Behavior

**As input component:** Passes text value as a `str` into the function.

**As output component:** Expects a `str` returned from function and sets textarea value to it.

### Initialization Parameters

- `value: str | Callable | None` - text to show in textbox (default: None)
- `type: ['text', 'password', 'email']` - textbox type (default: "text")
- `lines: int` - minimum number of line rows (default: 1)
- `max_lines: int | None` - maximum number of line rows (default: None)
- `placeholder: str | I18nData | None` - placeholder hint (default: None)
- `label: str | I18nData | None` - label for component (default: None)
- `info: str | I18nData | None` - additional component description (default: None)
- `every: Timer | float | None` - continuously recalculate value if function
- `inputs: Component | list[Component] | set[Component] | None` - inputs for value calculation
- `show_label: bool | None` - display label (default: None)
- `container: bool` - place in container (default: True)
- `scale: int | None` - relative size compared to adjacent components
- `min_width: int` - minimum pixel width (default: 160)
- `interactive: bool | None` - editable textbox (default: None)
- `visible: bool | 'hidden'` - component visibility (default: True)
- `elem_id: str | None` - HTML DOM id
- `autofocus: bool` - focus on load (default: False)
- `autoscroll: bool` - scroll to bottom on change (default: True)
- `elem_classes: list[str] | str | None` - HTML DOM classes
- `render: bool` - render in Blocks context (default: True)
- `key: int | str | tuple[int | str, ...] | None` - unique key for re-render
- `preserved_by_key: list[str] | str | None` - preserved parameters (default: "value")
- `text_align: ['left', 'right'] | None` - text alignment
- `rtl: bool` - right-to-left text direction (default: False)
- `buttons: list['copy'] | list[Button] | None` - buttons to show
- `max_length: int | None` - maximum number of characters
- `submit_btn: str | bool | None` - submit button (default: False)
- `stop_btn: str | bool | None` - stop button (default: False)
- `html_attributes: InputHTMLAttributes | None` - HTML attributes

### Event Listeners

- `.change(fn, ...)` - triggered when value changes
- `.input(fn, ...)` - triggered when user changes value
- `.select(fn, ...)` - triggered when user selects/deselects
- `.submit(fn, ...)` - triggered when user presses Enter
- `.focus(fn, ...)` - triggered when focused
- `.blur(fn, ...)` - triggered when unfocused
- `.stop(fn, ...)` - triggered when media ends
- `.copy(fn, ...)` - triggered when user copies content

### Shortcuts

- `gradio.Textbox` or `"textbox"` - default values
- `gradio.TextArea` or `"textarea"` - lines=7

---

## Button

```
gr.Button()
```

### Description

Creates a button that can be assigned arbitrary `.click()` events.

### Behavior

**As input component:** Passes the `str` corresponding to the button label when clicked.

**As output component:** Expects a string corresponding to the button label.

### Initialization Parameters

- `value: str | Callable` - button text (default: "Run")
- `every: Timer | float | None` - continuously recalculate value if function
- `inputs: Component | list[Component] | set[Component] | None` - inputs for value calculation
- `variant: ['primary', 'secondary', 'stop', 'huggingface']` - button style (default: "secondary")
- `size: ['sm', 'md', 'lg']` - button size (default: "lg")
- `icon: str | pathlib.Path | None` - icon file URL or path
- `link: str | None` - URL to open when clicked
- `link_target: ['_self', '_blank', '_parent', '_top']` - link target (default: "_self")
- `visible: bool | 'hidden'` - component visibility (default: True)
- `interactive: bool` - enabled/disabled state (default: True)
- `elem_id: str | None` - HTML DOM id
- `elem_classes: list[str] | str | None` - HTML DOM classes
- `render: bool` - render in Blocks context (default: True)
- `key: int | str | tuple[int | str, ...] | None` - unique key for re-render
- `preserved_by_key: list[str] | str | None` - preserved parameters (default: "value")
- `scale: int | None` - relative size compared to adjacent components
- `min_width: int | None` - minimum pixel width

### Event Listeners

- `.click(fn, ...)` - triggered when button is clicked

### Shortcuts

- `gradio.Button` or `"button"` - default values
- `gradio.ClearButton` or `"clearbutton"` - clear button
- `gradio.DeepLinkButton` or `"deeplinkbutton"` - deep link button
- `gradio.DuplicateButton` or `"duplicatebutton"` - duplicate button
- `gradio.LoginButton` or `"loginbutton"` - login button

---

## File

```
gr.File()
```

### Description

Creates a file component that allows uploading one or more generic files (when used as an input) or displaying generic files or URLs for download (as output).

### Behavior

**As input component:** Passes the file as a `str` or `bytes` object, or a list of `str` or list of `bytes` objects, depending on `type` and `file_count`.

**As output component:** Expects a `str` filepath or URL, or a `list[str]` of filepaths/URLs.

### Initialization Parameters

- `value: str | list[str] | Callable | None` - default file(s) to display (default: None)
- `file_count: ['single', 'multiple', 'directory']` - file count mode (default: "single")
- `file_types: list[str] | None` - allowed file extensions or types (default: None)
- `type: ['filepath', 'binary']` - return type (default: "filepath")
- `label: str | I18nData | None` - label for component (default: None)
- `every: Timer | float | None` - continuously recalculate value if function
- `inputs: Component | list[Component] | set[Component] | None` - inputs for value calculation
- `show_label: bool | None` - display label (default: None)
- `container: bool` - place in container (default: True)
- `scale: int | None` - relative size compared to adjacent components
- `min_width: int` - minimum pixel width (default: 160)
- `height: int | str | float | None` - component height
- `interactive: bool | None` - allow file upload (default: None)
- `visible: bool | 'hidden'` - component visibility (default: True)
- `elem_id: str | None` - HTML DOM id
- `elem_classes: list[str] | str | None` - HTML DOM classes
- `render: bool` - render in Blocks context (default: True)
- `key: int | str | tuple[int | str, ...] | None` - unique key for re-render
- `preserved_by_key: list[str] | str | None` - preserved parameters (default: "value")
- `allow_reordering: bool` - allow file reordering by drag-and-drop (default: False)
- `buttons: list[Button] | None` - buttons to show

### Event Listeners

- `.change(fn, ...)` - triggered when value changes
- `.input(fn, ...)` - triggered when user changes value
- `.select(fn, ...)` - triggered when user selects/deselects
- `.clear(fn, ...)` - triggered when user clears file
- `.upload(fn, ...)` - triggered when user uploads file
- `.delete(fn, ...)` - triggered when user deletes file
- `.download(fn, ...)` - triggered when user downloads file

### Shortcuts

- `gradio.File` or `"file"` - single file
- `gradio.Files` or `"files"` - multiple files

---

## Layout Components

### Row

```
gr.Row()
```

Creates a horizontal row layout for components.

### Column

```
gr.Column()
```

Creates a vertical column layout for components.

### Tab

```
gr.Tab()
```

Creates a tab for grouping components.

### Accordion

```
gr.Accordion()
```

Creates a collapsible accordion section.

### Group

```
gr.Group()
```

Creates a group for related components.

---

## Streaming Support

Gradio 6.x supports streaming for real-time updates using `yield` in generator functions:

```python
def streaming_function(input_text):
    for chunk in process_in_chunks(input_text):
        yield chunk

demo = gr.Interface(
    fn=streaming_function,
    inputs=gr.Textbox(),
    outputs=gr.Textbox()
)
```

For streaming in Blocks:

```python
with gr.Blocks() as demo:
    input_text = gr.Textbox()
    output_text = gr.Textbox()
    btn = gr.Button("Generate")
    
    btn.click(
        streaming_function,
        input_text,
        output_text
    )
```

Streaming parameters:
- `time_limit: int` - stream time limit in seconds (default: 30)
- `stream_every: float` - stream chunk latency in seconds (default: 0.5)
