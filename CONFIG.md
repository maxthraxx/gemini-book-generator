# Configuration (`config.yaml`)

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
