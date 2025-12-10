# Mouse Clock Tool

The "Mouse Clock" is a Python-based tool that allows users to reposition their mouse cursor using voice commands. The tool maps the hours on a standard 12-hour clock to the first 12 letters of the English alphabet (A-L) and includes concentric colored circles for precise control.

## Features

- **Clock Representation**: Displays 12 positions labeled A to L, corresponding to 1 o'clock through 12 o'clock.
- **Concentric Circles**: Five colored circles (Red, Blue, Pink, Green, Yellow) that users can specify to control the mouse's distance from the center.
- **Averaging Input**: Users can combine multiple letters and colors to calculate a midpoint for more precise mouse positioning.
- **History and Undo**: Maintains a history of mouse positions, allowing users to revert to previous positions.
- **Talon Voice Integration**: Works seamlessly with the Talon voice control system, recognizing commands for letters and colors.

## Installation

1. Navigate to your Talon Voice user folder: usually `/Users/<User Name>/.talon/user/<intended subfolder>`

2. Clone the repository:
   ```
   git clone <repository-url>
   cd mouse-clock
   ```

## Usage

Talon should hot reload all the mouse-clock related commands. Turn on Talon Voice and say the commands to test functionality.

Once running, you can use voice commands to control the mouse. For example:

- Saying "blue A" will move the mouse to the intersection of the blue circle and the A position.
- Saying "pink pink red C" will average the positions and move the mouse accordingly

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
