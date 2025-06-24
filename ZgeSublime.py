import sublime
import sublime_plugin
import subprocess
import os
import re

# Only enable the context menu for files with the .zgeproj extension
def is_zgeproj(view):
    file_name = view.file_name()
    return file_name and file_name.endswith(".zgeproj")

# Build and run ZGE project
class ZgeRunProjectCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return is_zgeproj(self.view)

    def run(self, edit):
        # Get full path of current file
        project_path = self.view.file_name()

        # Create output .exe path in the same folder
        exe_path = os.path.splitext(project_path)[0] + ".exe"

        # Load path from settings
        settings = sublime.load_settings("ZgeSublime.sublime-settings")
        zge_editor = settings.get("zge_editor_path", "")

        # Display error message if ZGameEditor.exe isn't found
        if not os.path.isfile(zge_editor):
            sublime.error_message("ZGameEditor.exe not found:\n{}".format(zge_editor))
            return

        # Auto-save before building
        self.view.run_command("save")

        # Command to run
        cmd = [zge_editor, "/b", project_path, exe_path]

        # Build the project and wait for it to finish
        build_proc = subprocess.Popen(cmd)
        build_proc.wait()

        # Run the project
        if os.path.isfile(exe_path):
            subprocess.Popen([exe_path])
        else:
            sublime.error_message("Build failed: EXE not created.")

class ZgeFoldDataCommand(sublime_plugin.TextCommand):
    """
    Sublime Text plugin to toggle the collapsed (folded) state of the
    content within imported data XML tags.

    If the content is currently unfolded, it will fold it, displaying '...'.
    If the content is currently folded, it will unfold it, revealing the content.
    """
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
