# ZgeSublime

A [Sublime Text](https://www.sublimetext.com/) plugin to build and run `.zgeproj` files directly from the editor.

## Installation

1. In Sublime Text, go to `Preferences > Browse Packages...`
2. This opens the Packages folder. Clone or copy the ZgeSublime folder into it.

## Configuration

Edit the `ZgeSublime.sublime-settings` file and set the path to your `ZGameEditor.exe`.

Default path: `C:/Dropbox/System/ZGameEditor/ZGameEditor.exe`

## Usage

Open your `.zgeproj` file in Sublime Text.  
Right-click in the editor to open the context menu and choose **ZGameEditor**:

- **Run project**  
This saves the file, then builds and runs your project.  
You can also press `Ctrl+Enter` to run the same command.

## Planned Features

- Commands to auto-close or expand specific XML tags
- Open `<Expression>` blocks in external views for better clarity
