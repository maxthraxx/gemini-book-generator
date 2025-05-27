# AI Book Weaver 📚🤖

AI Book Weaver is a powerful Python-based command-line tool that automates the creation of entire books, from initial concept to a fully formatted DOCX manuscript. It leverages Large Language Models (LLMs) like Google's Gemini and local Ollama instances to generate diverse content, including titles, chapter outlines, detailed section text, front and back matter, and even marketing materials. The script also features sophisticated LaTeX math-to-image rendering and advanced DOCX styling capabilities.

## Key Features

*   **Dual LLM Support:** Seamlessly integrates with Google Gemini (cloud-based) and Ollama (local) for flexible content generation.
*   **Comprehensive Content Generation:**
    *   **Core Elements:** Book title, subtitle, author details (name and gender can be auto-generated or specified).
    *   **Creative Seeds:** Random or user-defined main topic, setting, and writing tone.
    *   **Narrative Aids:** Character lists, particularly useful for fiction.
    *   **Structural Components:** Chapter outlines, concise chapter summaries, and detailed section-by-section content.
    *   **Front Matter:** Title page, copyright page, dedication, foreword, preface, and acknowledgements.
    *   **Back Matter:** Appendix (with structured subsections), "About the Author" section.
    *   **Promotional Content:** Engaging book blurb and an overall book summary.
*   **LaTeX Math Equation Rendering:** Converts LaTeX mathematical expressions (both inline `$...$` and display `$$...$$`) into high-quality PNG images for embedding in the DOCX.
*   **Advanced DOCX Output:**
    *   Produces a professionally formatted DOCX file.
    *   Highly customizable styles for fonts, font sizes, page layouts (e.g., 6x9, A4).
    *   Complex page numbering: Roman numerals for front matter, decimal for main content and back matter, with correct section breaks and odd-page starts.
    *   Print-ready features like mirrored margins and gutter settings.
    *   Accurate handling of headings, multi-level lists, tables, code blocks, and blockquotes.
*   **Dedicated Marketing Document:** Generates a separate DOCX file containing book details, the blurb, overall summary, and author biography for promotional use.
*   **Intelligent Caching:** Caches LLM API responses to significantly speed up subsequent runs and reduce API call costs. Cache is organized by LLM model and book topic.
*   **Flexible Configuration:** Driven by a `config.yaml` file for easy customization of generation parameters, API settings, and styling.
*   **Automated Fallbacks:** Capable of auto-generating missing essential information like topic, author details, or setting if not provided in the configuration.
*   **Fiction/Non-Fiction Awareness:** Adapts content generation (e.g., character lists, chapter structure) based on whether the book is identified as fiction or non-fiction.

## Prerequisites

*   **Python:** Version 3.8 or higher.
*   **PIP:** Python package installer (usually comes with Python).
*   **LaTeX Distribution:** A working LaTeX installation is required for rendering mathematical equations using `matplotlib`'s `usetex` feature. This includes packages like `amsmath` and `amssymb`.
    *   **Windows:** MiKTeX
    *   **macOS:** MacTeX
    *   **Linux:** TeX Live (e.g., `sudo apt-get install texlive-latex-extra texlive-fonts-recommended dvipng cm-super`)
*   **Google Gemini API Key:** Required if using the "gemini" provider.
*   **Ollama Server:** Required if using the "ollama" provider. Ensure the Ollama server is running and the desired models are pulled (e.g., `ollama pull llama3`).

## Setup Instructions

1.  **Clone the Repository (if applicable):**
    If you've obtained this project as a Git repository:
    *   ```bash
        git clone <repository-url>
        cd <repository-directory>
        ```

2.  **Install Python Dependencies:**
    The project relies on several Python libraries. You can install them using pip:
    *   ```bash
        pip install google-generativeai PyYAML python-docx matplotlib python-dotenv lxml requests transformers Pillow random_words Markdown pymdown-extensions
        ```
    *(Consider creating a `requirements.txt` file for easier dependency management.)*

3.  **Set Up API Keys (for Gemini):**
    If you plan to use Google Gemini, create a `.env` file in the project's root directory. Add your API key to this file:
    *   ```env
        GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
        ```

4.  **Verify LaTeX Installation:**
    Ensure your LaTeX distribution is correctly installed and its binaries are in your system's PATH. Test by compiling a simple LaTeX document if unsure.

## Configuration (`config.yaml`)

The behavior of AI Book Weaver is primarily controlled by the `config.yaml` file. Below is an overview of its main sections and common options.

*   **`api_settings`**: Configures the LLM provider and caching.
    *   `provider`: Set to `"gemini"` or `"ollama"`.
    *   `gemini`:
        *   `model`: E.g., `"gemini-1.5-flash-latest"`.
        *   `temperature`: Controls randomness (e.g., `0.8`).
        *   `max_retries`, `retry_delay_seconds`: For API call resilience.
        *   `safety_settings`: Configure content safety filters.
    *   `ollama`:
        *   `base_url`: E.g., `"http://localhost:11434"`.
        *   `model`: E.g., `"llama3"`.
        *   `temperature`: E.g., `0.7`.
        *   `tokenizer_model`: (Optional) For client-side token counting, e.g., `"NousResearch/Llama-3-8B-Instruct-hf"`.
        *   `context_window_size`: (Optional) `num_ctx` for Ollama.
    *   `base_cache_dir`: Path for API call caching (default: `"api_cache"`).
    *   `default_max_retries`, `default_retry_delay_seconds`: Global retry defaults.

*   **`generation_params`**: Controls the content and structure of the book.
    *   `main_topic`: (Optional) If empty, a random topic is generated.
    *   `random_topic_seed`: (Optional) Seed for random topic generation.
    *   `setting`: (Optional) Book's setting. Auto-generated if empty.
    *   `author_name`: (Optional) Auto-generated if empty.
    *   `author_gender`: (Optional) `male`, `female`, `other`. Determined or randomized if empty.
    *   `writing_tone`: (Optional) E.g., `"academic, informative, yet engaging"`. Auto-generated if empty.
    *   `book_title`: (Optional) Auto-generated if empty.
    *   `book_subtitle`: (Optional) Auto-generated if empty.
    *   `length_modifier`: (Optional) Adverb like `"very"`, `"moderately"` to influence summary/outline length.
    *   `num_chapters_fallback`: Default number of chapters if outline generation fails.
    *   `generate_character_list`: (Optional, boolean) `true` to force, `false` to disable. If unset, generated for fiction.
    *   `generate_foreword`: (Optional, boolean, default: `true`).
    *   `generate_acknowledgements`: (Optional, boolean, default: `true`).
    *   `generate_appendix`: (Optional, boolean, default: `true`).
    *   `include_about_author_in_main_book`: (Optional, boolean, default: `true`).

*   **`style_params`**: Defines the appearance of the output DOCX.
    *   `font_name`: Default `"Times New Roman"`.
    *   `font_size`: Default `12` (points).
    *   `page_size_preset`: `"6x9"` (inches) or `"A4"`.
    *   `margins_mm`: `top`, `bottom`, `left` (outside), `right` (inside), `gutter`.
    *   `inline_math_height_multiplier`: For scaling inline math images (default: `1.05`).
    *   `display_math_height_inches`: Default height for display math images (default: `0.375`).
    *   `inline_math_vertical_offset_half_points`: Fine-tunes vertical alignment of inline math (default: `-4`).

*   **`output_dir`**: Directory for the generated book files (default: `"output"`).

*   **`debug_options`**:
    *   `verbose_debug`: `true` or `false`. Enables detailed LLM call logging and streams responses to the console.
    *   `save_intermediate_html`: `true` to save the HTML output from Markdown conversion (useful for debugging formatting issues).

**Example `config.yaml` Snippet:**
*   ```yaml
    api_settings:
      provider: "gemini" # or "ollama"
      gemini:
        model: "gemini-1.5-flash-latest"
        temperature: 0.85
      # ollama:
      #   base_url: "http://localhost:11434"
      #   model: "llama3"
      #   temperature: 0.7
      base_cache_dir: "api_cache" # Cache stored here

    generation_params:
      # main_topic: "The Secret Life of Urban Foxes" # Leave empty to auto-generate
      # author_name: "Willow Whisperwind" # Leave empty to auto-generate
      length_modifier: "concise"
      generate_character_list: true # Example for a fictional book

    style_params:
      font_name: "Garamond"
      font_size: 11.5
      page_size_preset: "6x9"
      margins_mm:
        top: 19
        bottom: 25
        left: 13  # Outside margin
        right: 19 # Inside margin (for binding)
        gutter: 6 # Space for binding

    output_dir: "my_books" # Output files will go here

    debug_options:
      verbose_debug: true
      save_intermediate_html: true
    ```

## How to Run

Execute the script from your terminal:
*   ```bash
    python generate_book.py
    ```
The script will:
1.  Load `config.yaml`.
2.  Set up the environment and API connections.
3.  Generate content for each part of the book, using cached data if available.
4.  Assemble the main DOCX file and the marketing DOCX file.
5.  Save all outputs to the directory specified in `output_dir`.

## Output Files

The script generates the following in the specified `output_dir`:

*   **`{SanitizedBookTitle}.docx`**: The main, fully formatted book manuscript.
*   **`{SanitizedBookTitle}_Marketing.docx`**: A supplementary document with the book blurb, overall summary, author bio, and other key details for promotional purposes.
*   **`{SanitizedBookTitle}_Summary.md`**: The overall book summary in Markdown format.

**Cache and Temporary Files:**
*   **API Cache:** Located in the `base_cache_dir` (e.g., `api_cache/`), sub-organized by LLM model name and then by a unique identifier for the book's main topic (sanitized name + hash). This significantly speeds up re-runs.
*   **Equation Images:** Rendered LaTeX equations (as PNGs) are stored within a dedicated `equation_images` subdirectory inside the topic-specific cache folder.
*   **Intermediate HTML (Optional):** If `save_intermediate_html` is true, HTML files generated during Markdown-to-DOCX conversion are saved in a `debug_html` subdirectory within the topic-specific cache folder.

## LLM Provider Details

*   **Google Gemini:**
    *   Uses the `google-generativeai` Python library.
    *   Requires a `GEMINI_API_KEY` to be set in a `.env` file at the project root.
    *   Configuration options (model, temperature, safety settings) are in `config.yaml` under `api_settings.gemini`.
*   **Ollama:**
    *   Communicates with a local Ollama server instance.
    *   Ensure Ollama is running and accessible at the `base_url` specified in `config.yaml`.
    *   The desired model (e.g., `llama3`) must be pulled to your Ollama instance (`ollama pull <model_name>`).
    *   Configuration options (model, temperature, context window) are in `config.yaml` under `api_settings.ollama`.

## Caching Mechanism

To optimize performance and reduce API usage:
*   LLM API responses are cached locally.
*   Cache files are stored in JSON format, containing the prompt and the corresponding response.
*   The cache directory is structured as: `<base_cache_dir>/<sanitized_model_name>/<sanitized_topic_name_topic_hash>/`.
*   Cache filenames are generated using a hash of the prompt text, often prefixed by a context hint (e.g., `summary_chapter_title_xyz`).
*   To force regeneration of content for a specific book project or model, you can delete the relevant subdirectory within the `base_cache_dir`.

## Customization Tips

*   **Content Focus:** The most impactful customization comes from defining `main_topic`, `setting`, `author_name`, `author_gender`, and `writing_tone` in `generation_params` of `config.yaml`.
*   **Styling:** Modify `style_params` in `config.yaml` to change fonts, page sizes, and margins for the DOCX output.
*   **Prompt Engineering:** For fine-grained control over generated content, you can directly edit the prompt strings within the `generate_book.py` script (e.g., in functions like `generate_section_content`, `generate_chapter_summary`, etc.).
*   **LLM Selection:** Experiment with different LLM providers (`gemini`, `ollama`) and models (e.g., `gemini-1.5-pro-latest`, `llama3:70b`) and their parameters (`temperature`) in `api_settings` to achieve desired results.

## Troubleshooting & Important Notes

*   **LaTeX Math Rendering Issues:**
    *   A complete LaTeX distribution (like MiKTeX, MacTeX, or TeX Live) including `amsmath` and `amssymb` packages must be installed and accessible via your system's PATH.
    *   The script uses `matplotlib`'s `mathtext` engine, which emulates TeX. While it doesn't always require a full TeX system for basic rendering, having one ensures access to standard TeX fonts and robust parsing, especially since `text.usetex` is enabled.
    *   If math images are missing or look incorrect, check the console output for errors from `matplotlib` or LaTeX.
*   **API Errors & Quotas:**
    *   **Gemini:** Double-check your `GEMINI_API_KEY` for correctness and ensure your Google Cloud project has the Generative Language API enabled and sufficient quota.
    *   **Ollama:** Confirm the Ollama server is running, the specified model is downloaded (`ollama list`), and the `base_url` in `config.yaml` is correct. Check Ollama server logs for more details.
*   **File Permissions:** The script needs write access to the `output_dir` and the `base_cache_dir`.
*   **Generation Duration:** Creating a full book is computationally intensive and can take a considerable amount of time, particularly on the first run when no cache exists. Subsequent runs for the same topic and model will be much faster.
*   **Content Quality & Iteration:** The quality of the AI-generated text is dependent on the chosen LLM and the effectiveness of the prompts. Be prepared to iterate on `config.yaml` settings, or even the prompts in the script, to refine the output.
*   **Python Environment:** Using a virtual environment (e.g., `venv`, `conda`) is highly recommended to manage dependencies and avoid conflicts.
