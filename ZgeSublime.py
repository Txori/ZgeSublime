import sublime
import sublime_plugin
import subprocess
import os
import re

def is_zgeproj(view):
    """
    Checks if the current view's file has a '.zgeproj' extension.
    This is used to enable/disable commands in the context menu.
    """
    file_name = view.file_name()
    return file_name and file_name.endswith(".zgeproj")

def _run_zge_command(view, args, wait_for_completion=False):
    """
    Helper function to handle common setup and command execution for ZGE plugin commands.

    This function performs the following steps:
    1. Gets the full path of the current project file.
    2. Loads the ZGameEditor.exe path from Sublime Text settings.
    3. Validates if the ZGameEditor.exe path exists. If not, displays an error.
    4. Auto-saves the current view before executing the command.
    5. Constructs and executes the command using subprocess.Popen.
    6. Optionally waits for the process to complete.

    Args:
        view (sublime.View): The current Sublime Text view object.
        args (list): A list of arguments specific to the ZGE command (e.g., ["/b", project_path, exe_path]
                     for building, or ["/o", project_path] for opening).
        wait_for_completion (bool, optional): If True, the function will wait for the
                                              subprocess to finish before returning.
                                              Defaults to False.

    Returns:
        subprocess.Popen or None: The Popen object if the command was successfully
                                  executed, None if there was an error (e.g., editor not found).
    """
    project_path = view.file_name()

    # Load ZGE editor path from settings
    settings = sublime.load_settings("ZgeSublime.sublime-settings")
    zge_editor = settings.get("zge_editor_path", "")

    # Display error message if ZGameEditor.exe isn't found
    if not os.path.isfile(zge_editor):
        sublime.error_message("ZGameEditor.exe not found:\n{}".format(zge_editor))
        return None

    # Auto-save before running the command to ensure latest changes are included
    view.run_command("save")

    # Construct the full command list
    cmd = [zge_editor] + args

    try:
        # Execute the command
        proc = subprocess.Popen(cmd)
        if wait_for_completion:
            proc.wait() # Wait for the process to complete if required (e.g., for build operations)
        return proc
    except Exception as e:
        # Catch any errors during subprocess execution
        sublime.error_message("Error executing ZGE command: {}".format(e))
        return None

class ZgeRunProjectCommand(sublime_plugin.TextCommand):
    """
    Sublime Text plugin command to build and run a ZGE project.
    It uses the ZGameEditor.exe to build the current .zgeproj file
    into an executable and then runs the generated executable.
    """
    def is_enabled(self):
        return is_zgeproj(self.view)

    def run(self, edit):
        project_path = self.view.file_name()
        # Create the output .exe path in the same directory as the project file
        exe_path = os.path.splitext(project_path)[0] + ".exe"

        # Use the helper function to build the project.
        # We wait for completion here because we need the build to finish before running the EXE.
        build_proc = _run_zge_command(self.view, ["/b", project_path, exe_path], wait_for_completion=True)

        if build_proc is None:
            # If the helper function returned None, an error occurred (e.g., editor not found)
            return

        # After building, check if the executable was created and run it
        if os.path.isfile(exe_path):
            try:
                subprocess.Popen([exe_path])
            except Exception as e:
                sublime.error_message("Error running project EXE: {}".format(e))
        else:
            sublime.error_message("Build failed: EXE not created at '{}'.".format(exe_path))

class ZgeEditProjectCommand(sublime_plugin.TextCommand):
    """
    Sublime Text plugin command to open the current .zgeproj file in ZGameEditor.
    It uses the ZGameEditor.exe with the '/o' flag to open the project for editing.
    """
    def is_enabled(self):
        return is_zgeproj(self.view)

    def run(self, edit):
        project_path = self.view.file_name()

        # Use the helper function to open the project in the ZGE editor.
        # We don't need to wait for completion here, as ZGE can open in the background.
        _run_zge_command(self.view, [project_path])

class ZgeFoldDataCommand(sublime_plugin.TextCommand):
    """
    Sublime Text plugin to toggle the collapsed (folded) state of the
    content within imported data XML tags.

    If the content is currently unfolded, it will fold it, displaying '...'.
    If the content is currently folded, it will unfold it, revealing the content.
    """
    def is_enabled(self):
        return is_zgeproj(self.view)

    def run(self, edit):
        # 1. Get the entire content of the current view.
        content = self.view.substr(sublime.Region(0, self.view.size()))

        # 2. Define the regular expression pattern to find the tags.
        #    This regex remains the same as it correctly identifies the start and end
        #    of the content that needs to be folded/unfolded.
        pattern = re.compile(
            r'(<(BitmapFile|FileEmbedded|Icon|MeshData|MusicFile|SampleData|SpriteData|Values)[^>]*>)(.*?)(</\2>)',
            re.DOTALL
        )

        # 3. Initialize a list to store the regions that are candidates for folding/unfolding.
        regions_to_toggle = []

        # 4. Iterate over all matches found by the regex.
        for match in pattern.finditer(content):
            # Extract the start and end positions (character offsets) of the matched groups.
            open_tag_end = match.end(1)    # Position right after '>' of the opening tag.
            close_tag_start = match.start(4) # Position right before '<' of the closing tag.

            # Create a sublime.Region object for the content to be toggled.
            fold_region = sublime.Region(open_tag_end, close_tag_start)

            # Only consider regions with actual content to toggle.
            if fold_region.begin() < fold_region.end():
                regions_to_toggle.append(fold_region)

        # If no relevant tags are found, there's nothing to do.
        if not regions_to_toggle:
            sublime.status_message("No data tags found to toggle.")
            # print("No regions found to toggle.") # Debug print
            return # Exit the function early

        # 5. Determine the current state of the folds.
        #    We check the first identified region. If it's folded, we assume the intent
        #    is to unfold all. Otherwise, the intent is to fold all.
        #    This is a simplification; for more robust toggling, you might check if *all*
        #    are folded, or only toggle individually if some are folded and some aren't.
        #    For this use case (collapsing/expanding entire blocks), checking one is usually sufficient.
        first_region_is_folded = self.view.is_folded(regions_to_toggle[0])

        if first_region_is_folded:
            # If the first region is folded, unfold all regions.
            self.view.unfold(regions_to_toggle)
            sublime.status_message("Unfolded {} data tags.".format(len(regions_to_toggle)))
            # print("Successfully unfolded {} regions.".format(len(regions_to_toggle))) # Debug print
        else:
            # If the first region is not folded, fold all regions.
            self.view.fold(regions_to_toggle)
            sublime.status_message("Folded {} data tags.".format(len(regions_to_toggle)))
            # print("Successfully folded {} regions.".format(len(regions_to_toggle))) # Debug print

class ZgeAddCodeSpacingCommand(sublime_plugin.TextCommand):
    """
    Sublime Text command to add specific line spacing and comments
    around CDATA sections within designated XML code tags.

    This command targets XML tags such as "BeforeInitExp", "Expression", etc.,
    and modifies their CDATA content to include "//" and two newlines
    after the CDATA opening, and two newlines and "//" before the CDATA closing.
    It now also preserves the original whitespace (newlines and indentation)
    surrounding the CDATA blocks.

    This version ensures consistency: it strips *only* any previously added
    plugin-specific "//" and associated newlines from the start and end of the
    CDATA content, then adds the standardized required prefix and suffix.
    User-defined comments beginning or ending with "//" will be preserved.
    """

    def run(self, edit):
        """
        Executes the command to modify the content of the current view.

        Args:
            edit (sublime.Edit): An object that represents a single, atomic
                                 undoable edit. All changes to the buffer
                                 must be performed via this object.
        """
        # Define the list of XML tags whose CDATA content should be modified.
        code_tags = [
            "BeforeInitExp",
            "Expression",
            "OnEmitExpression",
            "Source",
            "WhileExp"
        ]

        # Escape tag names for use in a regular expression to handle special characters.
        tag_pattern = '|'.join(re.escape(tag) for tag in code_tags)

        # Construct the regular expression pattern to find and capture all necessary parts:
        # Group 1: The entire opening XML tag (e.g., <Expression foo="bar">)
        #   - Group 2 (nested): The actual tag name (e.g., Expression)
        # Group 3: Whitespace between the opening XML tag and the CDATA opening delimiter.
        # Group 4: The content inside the CDATA block.
        # Group 5: Whitespace between the CDATA closing delimiter and the closing XML tag.
        # Group 6: The entire closing XML tag (e.g., </Expression>), using backreference \2.
        regex_pattern = (
            r'(<(' + tag_pattern + r')\b[^>]*>)'  # Group 1: Opening tag (captures Group 2: tag name)
            r'(\s*)'                             # Group 3: Whitespace *before* <![CDATA[
            r'<!\[CDATA\['
            r'(.*?)'                             # Group 4: Non-greedy match for the content *within* CDATA
            r'\]\]>'
            r'(\s*)'                             # Group 5: Whitespace *after* ]]>
            r'(</\2>)'                           # Group 6: Closing tag, using backreference to Group 2
        )

        # Compile the regex for better performance.
        # re.DOTALL ensures that '.*?' matches newline characters as well,
        # allowing it to capture multi-line CDATA content.
        pattern = re.compile(regex_pattern, re.DOTALL)

        # Get the entire content of the current view (the document being edited).
        full_region = sublime.Region(0, self.view.size())
        content = self.view.substr(full_region)

        # Find all occurrences of the pattern in the content.
        # Store them in a list before iterating in reverse to avoid issues
        # with region offsets caused by replacements.
        matches = list(pattern.finditer(content))

        # Define the exact prefix and suffix we want to enforce.
        standard_prefix = '//\n\n'
        standard_suffix = '\n\n//'

        # Patterns to *specifically* strip the plugin's own markers.
        # These patterns are now more precise to avoid removing user-defined comments.
        # It looks for "//" followed by exactly two newlines, optionally with surrounding whitespace.
        strip_prefix_pattern = re.compile(r'^\s*//\s*\n\n\s*')
        strip_suffix_pattern = re.compile(r'\s*\n\n\s*//\s*$')


        # Iterate through matches in reverse order to ensure that replacements
        # do not affect the start/end positions of subsequent matches.
        for m in reversed(matches):
            # Create a Sublime Text Region object corresponding to the full match.
            original_match_region = sublime.Region(m.start(), m.end())

            # Extract the captured groups.
            opening_tag = m.group(1)
            whitespace_before_cdata = m.group(3)
            cdata_content = m.group(4)
            whitespace_after_cdata = m.group(5)
            closing_tag = m.group(6)

            # --- Normalization Step ---
            # Attempt to remove *only* the plugin's specific prefix if it exists.
            # re.sub will only replace if the pattern matches at the beginning.
            stripped_content = strip_prefix_pattern.sub('', cdata_content, count=1)

            # Attempt to remove *only* the plugin's specific suffix if it exists.
            # re.sub will only replace if the pattern matches at the end.
            stripped_content = strip_suffix_pattern.sub('', stripped_content, count=1)

            # Do NOT use .strip() here, as it would remove legitimate leading/trailing
            # whitespace or comments from the user's original code.

            # --- Enforcement Step ---
            # Add the standardized prefix and suffix.
            # This ensures the output is consistent regardless of initial state,
            # and preserves other user comments.
            modified_cdata_inner_content = '{0}{1}{2}'.format(
                standard_prefix,
                stripped_content,
                standard_suffix
            )

            # Assemble the complete new string for the matched region,
            # preserving the captured whitespace around the CDATA block.
            new_full_string = '{0}{1}<![CDATA[{2}]]>{3}{4}'.format(
                opening_tag,
                whitespace_before_cdata,
                modified_cdata_inner_content,
                whitespace_after_cdata,
                closing_tag
            )

            # Replace the old content with the newly formatted content in the view.
            self.view.replace(edit, original_match_region, new_full_string)

        # Display a success message in the Sublime Text status bar.
        sublime.status_message("Code spacing standardized and comments preserved successfully!")
