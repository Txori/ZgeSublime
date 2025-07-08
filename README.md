# ZgeSublime

A [Sublime Text](https://www.sublimetext.com/) 4 plugin to build and run [ZGameEditor](https://www.zgameeditor.org/) projects directly from the editor.

## Installation

1. In Sublime Text, go to `Preferences > Browse Packages...`
2. This opens the Packages folder. Clone or copy the ZgeSublime folder into it.

## Configuration

Edit the `ZgeSublime.sublime-settings` file and set the path to your `ZGameEditor.exe`.

Default path: `C:/ZGameEditor/ZGameEditor.exe`

## Syntax Highlighting

The plugin includes custom syntax highlighting for `.zgeproj` files:

- The base is styled as standard XML
- ZExpression sections (`<Expression>`, `<WhileExp>`, etc.) use C#-like coloring
- Data sections (`<BitmapFile>`, `<MeshData>`, etc.) appear in grey for minimal visibility

The syntax should activate automatically when opening `.zgeproj` files. If it doesn't:

1. Open a `.zgeproj` file
2. Click the current syntax name in the bottom-right status bar (or use `Ctrl+Shift+P`)
3. Select "ZGameEditor" from the list

## Usage

Open your `.zgeproj` file in Sublime Text.  
Right-click in the editor to open the context menu and choose **ZGameEditor**:

- **Run project**  
This saves the file, then builds and runs your project.  
You can also press `Ctrl+Enter` to run the same command.

- **Edit project**
This saves the file, then opens the project in ZGameEditor.
When you save the file in ZGameEditor, it automatically updates the file in Sublime Text.
So this is very handy to add stuff in your project, then get back to Sublime Text.
You can also press `Ctrl+E` to run the same command.

- **Fold/Unfold data**  
This folds (or unfolds) all the XML data tags in your project, so you can focus only on the code.

- **Add code spacing**  
This will standardize spacing and adds comments within specific XML `<![CDATA[...]]>` sections, improving code readability.
Running multiple times will not add extra spacing; it normalizes the format.

For example, it will convert:
```
<Expression>
<![CDATA[float c1 = cos(X);]]>
</Expression>
```
To:
```
<Expression>
<![CDATA[//

float c1 = cos(X);

//]]>
</Expression>
```
