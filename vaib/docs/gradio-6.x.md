# Gradio 6.x Documentation

## Changelog Highlights for Gradio 6.x

### Version 6.8.0 (Feb 27, 2026)
- Latest release
- Bug fixes and improvements

### Version 6.7.0 (Feb 26, 2026)
- **Security Fix:** Fixed absolute path traversal issue on Windows with Python 3.13+ (CVE-2026-28414)
- Bug fixes and improvements

### Version 6.6.0 (Feb 17, 2026)
- Bug fixes and improvements

### Version 6.5.1 (Jan 29, 2026)
- Bug fixes and improvements

### Version 6.5.0 (Jan 28, 2026)
- Bug fixes and improvements

### Version 6.4.0 (Jan 22, 2026)
- Bug fixes and improvements

### Version 6.3.0 (Jan 10, 2026)
- Bug fixes and improvements

### Version 6.2.0 (Dec 19, 2025)
- Bug fixes and improvements

### Version 6.1.0 (Dec 9, 2025)
- Bug fixes and improvements

### Version 6.0.2 (Dec 2, 2025)
- Bug fixes and improvements

### Version 6.0.1 (Nov 25, 2025)
- Bug fixes and improvements

### Version 6.0.0 (Nov 21, 2025)
- **Major Release:** New features and improvements
- Breaking changes from 5.x

## Key Changes in Gradio 6.x

### Security Fixes
- **CVE-2026-28414:** Absolute path traversal issue on Windows with Python 3.13+ fixed in 6.7
- **CVE-2024-47871:** Insecure communication with share=True fixed in 5.0+
- **CVE-2024-47164:** Directory traversal bypass fixed in 5.0+
- **CVE-2024-47867:** Data validation vulnerability fixed in 5.0+
- **CVE-2024-47868:** Arbitrary file leaks fixed in 5.0+

### API Changes
- Various improvements to the Gradio API
- Enhanced streaming support via generator `yield`
- Better handling of file uploads
- Improved error messages

### UI Changes
- New components and styling options
- Better mobile responsiveness
- Enhanced settings panel

## Streaming Updates with Generator

Gradio 6.x supports streaming updates via generator `yield`:

```python
import gradio as gr

def generate_response():
    for i in range(10):
        yield f"Step {i}: Processing..."
        yield f"Step {i}: Complete!"

with gr.Blocks() as demo:
    output = gr.Textbox(label="Output")
    btn = gr.Button("Generate")
    
    btn.click(generate_response, outputs=output)
```

## File Upload Handling

Gradio 6.x provides improved file upload handling:

```python
import gradio as gr

def process_file(file):
    # Process the uploaded file
    return f"Processed: {file.name}"

with gr.Blocks() as demo:
    file_input = gr.File(label="Upload a file")
    output = gr.Textbox(label="Result")
    
    file_input.upload(process_file, outputs=output)
```

## Configuration Options

Gradio 6.x supports various configuration options:

```python
import gradio as gr

# Basic configuration
demo = gr.Interface(
    fn=lambda x: x,
    inputs="text",
    outputs="text",
    title="My App"
)

# Advanced configuration with Blocks
with gr.Blocks(title="My App") as demo:
    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(label="Input")
            output_text = gr.Textbox(label="Output")
    
    btn = gr.Button("Submit")
    btn.click(lambda x: x, inputs=input_text, outputs=output_text)
```

## Security Best Practices

1. **File Upload Security:**
   - Always validate file types and sizes
   - Use proper file path handling
   - Sanitize file names

2. **Path Traversal Prevention:**
   - Gradio 6.7+ includes fixes for path traversal issues
   - Ensure proper validation of file paths

3. **Share Mode Security:**
   - Avoid using `share=True` in production environments
   - Use proper authentication when sharing publicly

4. **Input Validation:**
   - Validate all user inputs
   - Sanitize user-provided content
   - Use proper error handling

## Migration from Gradio 5.x to 6.x

### Breaking Changes
- Some deprecated arguments have been removed
- Check the changelog for specific breaking changes
- Update your code accordingly

### New Features
- Enhanced streaming capabilities
- Better performance
- Improved error handling
- New UI components

## Documentation Links

- Official Documentation: https://www.gradio.app/docs/
- GitHub Repository: https://github.com/gradio-app/gradio
- PyPI: https://pypi.org/project/gradio/
