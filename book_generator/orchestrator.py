import hashlib
import logging
import pathlib
import sys
import time

import requests

from book_generator.config import load_config
from book_generator.constants import DEFAULT_WRITING_TONE
from book_generator.content_generator import (
    determine_gender_from_name,
    format_character_list_for_prompt,
    generate_back_matter,
    generate_book_blurb,
    generate_book_title,
    generate_chapter_outline,
    generate_chapter_summary,
    generate_character_list,
    generate_front_matter,
    generate_overall_summary,
    generate_random_gender,
    generate_random_name,
    generate_random_topic,
    generate_section_content,
    generate_section_titles,
    generate_setting,
    generate_writing_tone,
    is_book_non_fiction,
    save_summary_to_markdown,
)
from book_generator.docx_builder import assemble_docx, assemble_marketing_docx
from book_generator.llm_api import configure_gemini, setup_environment
from book_generator.utils import sanitize_filename


def run_generation_process():
    logging.info("Starting book generation process...")
    start_time = time.time()
    config = load_config()

    api_settings = config.get("api_settings", {})  # Get api_settings once

    # Determine API provider
    api_provider = api_settings.get("provider", "gemini")
    if api_provider == "gemini":
        api_key = setup_environment()  # This function exits if key not found
        configure_gemini(api_key)  # This function exits on error
        logging.info("Gemini API provider configured.")
    elif api_provider == "ollama":
        ollama_settings = config.get("ollama_settings", {})
        ollama_base_url = ollama_settings.get("base_url", "http://localhost:11434")
        try:
            logging.info(
                f"Ollama API provider selected. Attempting to connect to: {ollama_base_url}"
            )
            # Quick health check for Ollama server
            requests.get(
                f"{ollama_base_url.rstrip('/')}/api/tags", timeout=5
            ).raise_for_status()  # List models as a basic check
            logging.info(
                f"Successfully connected to Ollama server at {ollama_base_url}"
            )
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Error: Could not connect or communicate with Ollama server at {ollama_base_url}. Error: {e}. Please ensure Ollama is running and accessible."
            )
            sys.exit(1)
    else:
        logging.error(
            f"Unsupported API provider '{api_provider}' specified in config. Supported: 'gemini', 'ollama'. Exiting."
        )
        sys.exit(1)

    # --- Determine Output Directory ---
    # Default to a subdirectory named 'output' in the current working directory
    output_base_dir_str = config.get("output_dir", "output")
    output_base_dir = pathlib.Path(output_base_dir_str)
    # Create the base output directory if it doesn't exist
    try:
        output_base_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Using output directory: {output_base_dir.resolve()}")
    except Exception as e:
        logging.error(
            f"Failed to create output directory '{output_base_dir}': {e}. Exiting."
        )
        sys.exit(1)
    # Store the resolved path back in config for potential use elsewhere (optional)
    config["output_dir_resolved"] = output_base_dir
    # --- End Output Directory Setup ---

    # --- Determine Base Cache Directory ---
    base_cache_dir_from_config = api_settings.get("base_cache_dir", "api_cache")
    pathlib.Path(base_cache_dir_from_config).mkdir(parents=True, exist_ok=True)
    logging.info(f"Using base cache directory: {base_cache_dir_from_config}")

    # --- Determine Main Topic ---
    generation_params = config.setdefault("generation_params", {})  # Ensure exists

    # Check if main_topic is provided in the config
    if not generation_params.get("main_topic"):
        logging.info(
            "No 'main_topic' found in config. Attempting to auto-generate one."
        )
        random_topic = generate_random_topic(config)  # API call happens here
        if random_topic:
            generation_params["main_topic"] = random_topic
            logging.info(f"Auto-generated main_topic: '{random_topic}'")
        else:
            # If generation fails and it wasn't in config, we cannot proceed.
            logging.critical(
                "Fatal: Failed to auto-generate random topic and none provided in config. Exiting."
            )
            sys.exit(1)
    else:
        # If main_topic was provided in config, use it.
        logging.info(
            f"Using main_topic from config: '{generation_params['main_topic']}'"
        )
    # --- End Main Topic Determination ---

    # --- Construct Topic-Specific Cache Path AFTER topic is determined ---
    main_topic = generation_params["main_topic"]
    sanitized_topic = sanitize_filename(main_topic, 64)
    # Generate a short hash of the original topic for uniqueness
    topic_hash = hashlib.sha1(main_topic.encode("utf-8")).hexdigest()[:8]
    topic_dir_name = f"{sanitized_topic}_{topic_hash}"

    # --- Get and sanitize the model name for cache path ---
    if api_provider == "gemini":
        gemini_conf = api_settings.get("gemini", {})
        model_name_for_cache = gemini_conf.get("model", "gemini-2.0-flash-latest")
    elif api_provider == "ollama":
        ollama_conf = api_settings.get("ollama", {})
        model_name_for_cache = ollama_conf.get("model", "ollama_default_model")
    else:  # Should not happen due to earlier check
        model_name_for_cache = "unknown_api_provider_model"
    # Sanitize the model name to make it directory-safe, limit length
    sanitized_model_name = sanitize_filename(model_name_for_cache, 30)
    logging.info(f"Using model name for cache path: '{sanitized_model_name}'")

    # --- Create the cache path including the model name ---
    topic_specific_cache_dir = (
        pathlib.Path(base_cache_dir_from_config) / sanitized_model_name / topic_dir_name
    )  # Use pathlib
    logging.info(f"Topic-specific cache directory set to: {topic_specific_cache_dir}")
    # Update the config dictionary IN MEMORY so subsequent calls to call_llm_api use the right path
    config["cache_dir"] = str(
        topic_specific_cache_dir
    )  # Store as string if needed elsewhere
    # Ensure the specific directory exists
    topic_specific_cache_dir.mkdir(parents=True, exist_ok=True)

    # --- Define and Create Equation Image Directory HERE ---
    # Place equation images within the topic-specific, model-specific cache dir
    equation_image_dir = topic_specific_cache_dir / "equation_images"
    equation_image_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Equation image directory set to: {equation_image_dir}")
    # --- End Equation Image Directory Setup ---

    # Determine Setting
    if not generation_params.get("setting"):
        logging.info("No 'setting' found in config. Attempting to auto-generate one.")
        generated_setting = generate_setting(config)  # API call
        if generated_setting:
            generation_params["setting"] = generated_setting
            logging.info(f"Auto-generated setting: '{generated_setting[:100]}...'")
        else:
            # If generation fails and it wasn't in config, use a placeholder.
            logging.warning("Failed to auto-generate setting. Using placeholder.")
            generation_params["setting"] = "[Setting Generation Failed]"
    else:
        # If setting was provided in config, use it.
        logging.info(
            f"Using setting from config: '{generation_params['setting'][:100]}...'"
        )

    # Ensure setting exists even if generation failed or config was empty initially
    generation_params.setdefault(
        "setting", "[No Setting Provided or Generation Failed]"
    )
    # Log the final setting being used (could be from config, generated, or placeholder)
    logging.info(f"Final setting being used: '{generation_params['setting'][:100]}...'")

    # --- Determine Author Name and Gender ---
    author_name = generation_params.get("author_name", "").strip()
    author_gender = generation_params.get("author_gender", "").strip().lower()
    valid_genders = ["male", "female", "other"]

    if not author_name and not author_gender:
        logging.info("Author name and gender missing. Generating both...")
        # 1. Generate gender first
        generated_gender = generate_random_gender(config)  # Simple random choice
        logging.info(f"Randomly selected gender: {generated_gender}")
        # 2. Generate name based on gender
        generated_name = generate_random_name(config, generated_gender)  # API call
        if generated_name:
            author_name = generated_name
            author_gender = generated_gender
            generation_params["author_name"] = author_name
            generation_params["author_gender"] = author_gender
            logging.info(
                f"Generated Author: Name='{author_name}', Gender='{author_gender}'"
            )
        else:
            logging.critical(
                "Fatal: Failed to generate author name when both name and gender were missing. Exiting."
            )
            sys.exit(1)

    elif not author_name:
        logging.info(
            f"Author name missing. Generating name for specified gender: '{author_gender}'..."
        )
        if author_gender not in valid_genders:
            logging.warning(
                f"Provided gender '{author_gender}' is not standard ({valid_genders}). Attempting name generation anyway."
            )
            # Decide if you want to default the gender here or proceed. Let's proceed.

        generated_name = generate_random_name(config, author_gender)  # API call
        if generated_name:
            author_name = generated_name
            generation_params["author_name"] = author_name
            logging.info(
                f"Generated Author Name: '{author_name}' (Gender was '{author_gender}')"
            )
        else:
            logging.critical(
                f"Fatal: Failed to generate author name for gender '{author_gender}'. Exiting."
            )
            sys.exit(1)

    elif not author_gender:
        logging.info(
            f"Author gender missing. Attempting to determine gender from name: '{author_name}'..."
        )
        determined_gender = determine_gender_from_name(config, author_name)  # API call
        if determined_gender:
            author_gender = determined_gender
            generation_params["author_gender"] = author_gender
            logging.info(
                f"Determined Author Gender: '{author_gender}' (Name was '{author_name}')"
            )
        else:
            # If determination fails, you need a fallback. Using 'other' or exiting are options.
            logging.warning(
                f"Could not determine gender for '{author_name}'. Falling back to 'other'."
            )
            author_gender = "other"
            generation_params["author_gender"] = author_gender
            # Or, make it critical:
            # logging.critical(f"Fatal: Could not determine gender for name '{author_name}'. Exiting.")
            # sys.exit(1)

    else:
        # Both name and gender were provided
        logging.info(f"Using Author Name from config: '{author_name}'")
        if author_gender not in valid_genders:
            logging.warning(
                f"Author gender ('{author_gender}') from config is not standard ({valid_genders}). Using it anyway."
            )
        logging.info(f"Using Author Gender from config: '{author_gender}'")

    # Final check - ensure both have values before proceeding (should always pass if logic above is correct)
    if not generation_params.get("author_name"):
        logging.critical(
            "Fatal: Author name is still missing after processing. Exiting."
        )
        sys.exit(1)
    if not generation_params.get("author_gender"):
        logging.critical(
            "Fatal: Author gender is still missing after processing. Exiting."
        )
        sys.exit(1)

    logging.info(
        f"Final Author Details: Name='{generation_params['author_name']}', Gender='{generation_params['author_gender']}'"
    )
    # --- End Author Name and Gender Determination ---

    # Determine Writing Tone
    # Check if writing_tone is provided and not empty in the config
    writing_tone = generation_params.get("writing_tone", "").strip()

    if not writing_tone:
        # If not provided or empty, attempt to auto-generate it
        logging.info(
            "No 'writing_tone' found or it was empty in config. Attempting to auto-generate one."
        )
        generated_tone = generate_writing_tone(config)  # API call
        if generated_tone:
            writing_tone = generated_tone
            generation_params["writing_tone"] = (
                generated_tone  # Update config in memory
            )
            logging.info(f"Auto-generated writing tone: '{writing_tone}'")
        else:
            # If generation fails, fall back to the default
            writing_tone = DEFAULT_WRITING_TONE
            generation_params["writing_tone"] = (
                writing_tone  # Store default back in config
            )
            logging.warning(
                f"Failed to auto-generate writing tone. Using default: '{writing_tone}'"
            )
    else:
        # If it was provided in the config, use that value
        logging.info(f"Using writing_tone from config: '{writing_tone}'")

    # Ensure writing_tone has a value (either from config, generated, or default)
    if (
        not writing_tone
    ):  # Should ideally not happen due to fallback, but as a safeguard
        writing_tone = DEFAULT_WRITING_TONE
        generation_params["writing_tone"] = writing_tone
        logging.warning(
            f"Writing tone was still empty after checks. Using default: '{writing_tone}'"
        )

    logging.info(f"Final writing tone being used: '{writing_tone}'")
    # --- End Writing Tone Determination ---

    # --- Generate Core Book Structure ---
    # Check if book_title is provided in the config
    book_title_from_config = generation_params.get("book_title", "").strip()

    if book_title_from_config:
        book_title = book_title_from_config
        logging.info(f"Using Book Title from config: '{book_title}'")
    else:
        logging.info(
            "No 'book_title' found in config or it was empty. Attempting to auto-generate one."
        )
        book_title = generate_book_title(config)  # API call, exits on failure
        # generate_book_title exits if it fails or gets an empty title.
        # If it returns, it's a valid, cleaned title.
        logging.info(f"Successfully auto-generated Book Title: {book_title}")
        # Optionally, store the generated title back into config if desired for consistency
        # This ensures that if other parts of the code were to re-read it from config,
        # they'd see the generated one.
        generation_params["book_title"] = book_title

    # --- Determine if the book is fiction ---
    # This call will now use internal caching and set generation_params["is_fiction"]
    is_book_non_fiction(
        config, book_title
    )  # Ensures generation_params["is_fiction"] is set

    if generation_params.get(
        "is_fiction", False
    ):  # Default to False (non-fiction) if key is somehow missing
        logging.info(
            f"Book '{book_title}' has been identified as fiction. Detailed section generation within chapters will be skipped; chapter content will be generated as a single block."
        )
    else:
        logging.info(
            f"Book '{book_title}' has been identified as non-fiction (or type indeterminate, proceeding with detailed sections). Detailed sections will be generated within chapters."
        )
    # --- End Fiction Determination ---

    # --- Generate Character List (if enabled) ---
    generate_character_list(config, book_title)  # API call inside if enabled
    # The result (or None) is stored in config['generation_params']['character_list']

    # --- Generate Chapter Outline (potentially using characters) ---
    # Prepare character context string
    character_context_for_prompts = format_character_list_for_prompt(
        config["generation_params"].get("character_list")
    )

    chapter_titles = generate_chapter_outline(config, character_context_for_prompts)

    if chapter_titles:
        formatted_outline = "\n".join(
            f"{i+1}. {title}" for i, title in enumerate(chapter_titles)
        )
        logging.info(f"Generated Chapter Outline:\n{formatted_outline}")
    else:
        logging.error("Chapter outline generation resulted in no titles. Exiting.")
        sys.exit(1)  # Cannot proceed without chapters

    # --- Pass 1: Generate Chapter Summaries ---
    logging.info("--- Starting Pass 1: Generating Chapter Summaries ---")
    chapter_summaries = {}
    previous_summaries_list = []  # Keep track of summaries generated so far

    for i, chap_title in enumerate(chapter_titles):
        logging.info(f"--- Generating Summary for Chapter {i+1}: {chap_title} ---")

        # --- Create context string from previous summaries ---
        previous_summaries_context = ""
        if previous_summaries_list:
            # Format the context clearly, e.g., as a list
            context_parts = [
                f"- Chapter {idx+1}: {s}"
                for idx, s in enumerate(previous_summaries_list)
            ]
            previous_summaries_context = "\n".join(context_parts)
            logging.debug(
                f"Providing context of {len(previous_summaries_list)} previous summaries for chapter '{chap_title}'."
            )
        # --- End context creation ---

        # Pass the context to the generation function
        summary = generate_chapter_summary(
            config,
            chap_title,
            writing_tone,
            previous_summaries_context,
            character_context_for_prompts,
        )
        chapter_summaries[chap_title] = summary

        # --- Add the generated summary to the list for the next iteration's context ---
        # Only add valid, non-placeholder summaries to the context for subsequent chapters
        cleaned_summary_for_context = summary.strip()
        if cleaned_summary_for_context and not cleaned_summary_for_context.startswith(
            "Placeholder summary"
        ):
            previous_summaries_list.append(cleaned_summary_for_context)
        # --- End adding summary to list ---

    # --- Prepare Summary Context for subsequent prompts ---
    summary_context = "[No chapter summaries available]"  # Default
    summary_parts = []
    for i, chap_title in enumerate(chapter_titles):
        summary = chapter_summaries.get(chap_title, "").strip()
        if summary and not summary.startswith("Placeholder summary"):
            summary_parts.append(f"Chapter {i+1} ('{chap_title}'): {summary}")
    if summary_parts:
        summary_context = "Chapter summaries:\n" + "\n\n".join(summary_parts)
        logging.debug(f"Generated summary context:\n{summary_context}")
    else:
        logging.warning(
            "No valid chapter summaries generated to create summary context."
        )

    # --- Generate Overall Summary and Save to Markdown ---
    overall_summary_text = generate_overall_summary(config, book_title, summary_context)
    save_summary_to_markdown(book_title, overall_summary_text, output_base_dir)
    # --- End Overall Summary Generation ---

    # --- Generate Front/Back Matter & Marketing Content (using summaries) ---
    logging.info("--- Generating Front Matter, Back Matter, and Marketing Content ---")
    front_matter_content = generate_front_matter(
        config,
        book_title,
        generation_params["author_name"],
        writing_tone,
        summary_context,
    )  # Multiple API calls inside

    back_matter_content = generate_back_matter(
        config,
        book_title,
        generation_params["author_name"],
        generation_params["author_gender"],
        writing_tone,
        summary_context,
    )  # Multiple API calls inside

    main_filename_stem = sanitize_filename(book_title)
    if main_filename_stem != "sanitized_empty":
        blurb_text = generate_book_blurb(
            config, book_title, summary_context, writing_tone
        )  # API call
        assemble_marketing_docx(
            config,
            back_matter_content,
            blurb_text,
            summary_context,
            main_filename_stem,
            equation_image_dir,
            output_base_dir,
        )
    else:
        logging.error(
            f"Could not generate valid filename stem from title '{book_title}'. Skipping marketing DOCX."
        )

    # --- Pass 2: Generate Section Content (using summaries) ---
    logging.info("--- Starting Pass 2: Generating Section Content ---")
    body_matter = {}
    is_fiction_book = generation_params.get("is_fiction", False)  # Get the flag

    for i, chap_title in enumerate(chapter_titles):
        logging.info(f"--- Processing Chapter {i+1}: {chap_title} ---")
        chapter_summary = chapter_summaries.get(
            chap_title, f"Placeholder summary for chapter '{chap_title}'."
        )  # Use placeholder if missing
        body_matter[chap_title] = []  # Initialize with empty list for sections

        if is_fiction_book:
            logging.info(
                f"Book is fiction. Generating content for chapter '{chap_title}' as a single block."
            )
            # Use a generic title for the single content block of a fiction chapter
            fiction_section_title = "Narrative"  # Or "Chapter Content"
            chapter_content_as_single_block = generate_section_content(
                config,
                chap_title,  # chapter_title
                fiction_section_title,  # section_title (generic for fiction)
                1,  # section_num
                1,  # total_sections
                chapter_summary,
                writing_tone,
                character_context_for_prompts,
            )
            body_matter[chap_title].append(
                {
                    "title": "",
                    "content": chapter_content_as_single_block,
                }
            )
            if (
                not chapter_content_as_single_block
                or "Content generation failed" in chapter_content_as_single_block
            ):
                logging.warning(
                    f"Content generation potentially failed for fiction chapter '{chap_title}' (treated as single section)."
                )
        else:  # Non-fiction book, proceed with normal section generation
            # --- Call generate_section_titles with added context ---
            section_titles = generate_section_titles(
                config,
                chap_title,
                chapter_summary,
                chapter_titles,
                chapter_summaries,
                character_context_for_prompts,
            )

            if not section_titles:
                logging.warning(
                    f"No section titles generated for chapter '{chap_title}'. Adding chapter summary as placeholder content."
                )
                # Add chapter summary as content if no sections are generated
                body_matter[chap_title].append(
                    {"title": "Chapter Overview", "content": chapter_summary}
                )
                continue  # Skip to next chapter
            else:
                formatted_sections = "\n".join(
                    f"  {j+1}. {title}" for j, title in enumerate(section_titles)
                )
                logging.info(
                    f"Generated {len(section_titles)} section titles for chapter '{chap_title}':\n{formatted_sections}"
                )

            for j, sec_title in enumerate(section_titles):
                section_content = generate_section_content(
                    config,
                    chap_title,
                    sec_title,
                    j + 1,
                    len(section_titles),
                    chapter_summary,
                    writing_tone,
                    character_context_for_prompts,
                )
                body_matter[chap_title].append(
                    {"title": sec_title, "content": section_content}
                )
                if (
                    not section_content
                    or "Content generation failed" in section_content
                ):
                    logging.warning(
                        f"Content generation potentially failed for Chapter '{chap_title}', Section '{sec_title}'."
                    )

    logging.info("Finished generating all body matter.")

    # --- Assemble Final DOCX ---
    main_docx_filename = assemble_docx(
        config,
        front_matter_content,
        body_matter,
        back_matter_content,
        book_title,
        equation_image_dir,
        output_base_dir,
    )

    end_time = time.time()
    logging.info(
        f"Book generation process finished in {end_time - start_time:.2f} seconds."
    )
    if main_docx_filename:
        logging.info(f"Main book saved as: {main_docx_filename}")
    else:
        logging.error("Main book DOCX file failed to save.")
