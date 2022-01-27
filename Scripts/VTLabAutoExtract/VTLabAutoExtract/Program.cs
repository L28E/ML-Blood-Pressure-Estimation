using System;
using System.Diagnostics;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Conditions;
using FlaUI.Core.Definitions;
using FlaUI.UIA3;
using FlaUI.Core.Input;
using System.Drawing;

namespace VTLabAutoExtract
{
    internal class Program
    {
        const int LINE_DIST = 21;
        const int NUM_FILES = 956;

        const double FILE_WAIT = 2;
        const double EXPLORER_WAIT = 0.5;
        const double SAVE_WAIT = 1;

        const string BANNER = @"
    ___           __            ______       __                      __              
   /   |  __  __ / /_ ____     / ____/_  __ / /_ _____ ____ _ _____ / /_ ____   _____
  / /| | / / / // __// __ \   / __/  | |/_// __// ___// __ `// ___// __// __ \ / ___/
 / ___ |/ /_/ // /_ / /_/ /  / /___ _>  < / /_ / /   / /_/ // /__ / /_ / /_/ // /    
/_/  |_|\__,_/ \__/ \____/  /_____//_/|_| \__//_/    \__,_/ \___/ \__/ \____//_/     
                                                                                     ";
        static void Main(string[] args)
        {
            Application application;
            Window mainWindow;
            ConditionFactory conditionFactory = new ConditionFactory(new UIA3PropertyLibrary());

            // I like banners 
            Console.WriteLine(BANNER);
            Console.WriteLine("Uses automation tools to navigate a proprietary app to convert data files to a consistent format.\n\n"+
                "This program needs a little manual setup (to minimize dev effort). When you're ready for the manual setup, press any key");

            Console.ReadKey();
            Console.Clear();

            // Instruct the user through manual setup
            Console.WriteLine("1. You'll need to move ALL the log files to a flat directory.\n" +
                "Here's a powershell incantation which will do it for you. Make sure to replace the <source> and <dest> with file paths\n");

            Console.ForegroundColor = ConsoleColor.DarkYellow;
            Console.WriteLine("Get -ChildItem -Path <source> -Recurse -File -Include *.txt,*.bin | Copy-Item -Destination <dest>\n");
            Console.ResetColor();
            Console.WriteLine("There should be " + NUM_FILES.ToString() + " files in the destination. After you've done this, press any key to continue");
            
            Console.ReadKey();
            Console.Clear();

            Console.WriteLine("2. Open the VTLab app and select the folder you just made with every data file\n" +
                "Check that no filters are on.\n\n" +                
                "After you've done this, press any key to continue");

            Console.ReadKey();
            Console.Clear();

            // Check that VTLab is running, get its PID, and attach it to FLAUI
            // You should be able to launch it with FLAUI, but I was getting a cx_freeze error, same as winappdriver/appium 
            Process[] localByName = Process.GetProcessesByName("VTLab");
            if (localByName.Length == 0) {
                Console.WriteLine("Please start VTLab then rerun the program.");
                return;
            }
            Console.WriteLine("VTLab PID: " + localByName[0].Id.ToString());
            application = Application.Attach(localByName[0].Id);

            // Bring the app to the foreground
            mainWindow = application.GetMainWindow(new UIA3Automation());
            mainWindow.Focus();

            // Get buttons            
            AutomationElement menuItem = mainWindow.FindFirstDescendant(conditionFactory.ByName("File"));
            AutomationElement scrollDown = mainWindow.FindFirstDescendant(conditionFactory.ByAutomationId("DownButton"));

            // Get the file list and its bounds
            AutomationElement[] paneArr = mainWindow.FindAll(TreeScope.Descendants, conditionFactory.ByClassName("TkChild"));
            AutomationElement filePane = paneArr[18];  // There are 20 TKinter children(?). The 19th one is the pane listing files 
  
            int top = filePane.BoundingRectangle.Top;
            int left = filePane.BoundingRectangle.Left;
            int bottom = filePane.BoundingRectangle.Bottom;
            
            int cursorX = left + 5;
            int cursorY;

            for (int k = 0; k < NUM_FILES; k++)
            {
                if (k < 8)
                {                    
                    cursorY = top + 1 + LINE_DIST * k;                    
                }
                else
                {
                    scrollDown.AsButton().Click();                    
                    cursorY = bottom - 3;                                      
                }

                // Move mouse and double click to open
                Mouse.Position = new Point(cursorX, cursorY);                
                Mouse.DoubleClick();

                // Give it time to open then click "File"
                Wait.UntilInputIsProcessed(TimeSpan.FromSeconds(FILE_WAIT));
                menuItem.AsMenuItem().Click();  

                // Click "Save As"
                mainWindow.FindFirstDescendant(conditionFactory.ByAutomationId("23")).AsMenuItem().Click();
                Wait.UntilInputIsProcessed(TimeSpan.FromSeconds(EXPLORER_WAIT));

                // Click Save on the explorer dialog
                mainWindow.FindFirstDescendant(conditionFactory.ByName("Save")).AsMenuItem().Click();
                Wait.UntilInputIsProcessed(TimeSpan.FromSeconds(SAVE_WAIT));
            }
        }
    }
}
