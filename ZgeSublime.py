import sublime
import sublime_plugin
import subprocess
import os

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
        settings = sublime.load_settings("ZGameEditor.sublime-settings")
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
