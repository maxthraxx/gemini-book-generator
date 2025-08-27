# LLM Book Generator 📚🤖

AI Book Weaver is a powerful Python-based command-line tool that automates the creation of entire books, from initial concept to a fully formatted DOCX manuscript. It leverages Large Language Models (LLMs) like Google's Gemini and local Ollama instances to generate diverse content, including titles, chapter outlines, detailed section text, front and back matter, and even marketing materials.

## Features

*   **Dual LLM Support:** Seamlessly integrates with Google Gemini (cloud-based) and Ollama (local).
*   **Comprehensive Content Generation:** Creates everything from titles and chapter outlines to front and back matter.
*   **LaTeX Math Rendering:** Converts LaTeX math expressions into high-quality images.
*   **Advanced DOCX Styling:** Produces professionally formatted DOCX files with customizable styles.
*   **Intelligent Caching:** Caches LLM responses to speed up subsequent runs.
*   **Flexible Configuration:** Uses a `config.yaml` file for easy customization.

## Getting Started

### Prerequisites

*   Python 3.8+
*   A LaTeX distribution (e.g., [MiKTeX](https://miktex.org/), [MacTeX](https://www.tug.org/mactex/), [TeX Live](https://www.tug.org/texlive/))
*   A Google Gemini API key or a running Ollama instance.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your API key (for Gemini):**
    Create a `.env` file in the project root and add your Gemini API key:
    ```
    GEMINI_API_KEY="YOUR_API_KEY"
    ```

## How to Run

1.  **Configure your book:**
    Edit the `config.yaml` file to define your book's topic, author, style, and other parameters. For a detailed explanation of all the available options, see [CONFIG.md](CONFIG.md).

2.  **Run the script:**
    ```bash
    python main.py
    ```
    The generated book and marketing materials will be saved in the directory specified in `config.yaml` (default is `"output"`).

## Troubleshooting

*   **LaTeX Math Rendering Issues:** Ensure your LaTeX distribution is installed correctly and accessible from your system's PATH.
*   **API Errors:** Double-check your API keys and ensure that your LLM provider (Gemini or Ollama) is running and accessible.
*   **File Permissions:** Make sure the script has write access to the output and cache directories.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under GPLv3. See the [LICENSE](LICENSE) file for details.
