RFID-Reader-GUI
===============

This WISP demo application is currently only supported on Ubuntu. To get started follow the installation guide and quick start below.

<h1>Installation Guide</h1>

1. Open the terminal and begin by first installing Python 2.7.x <br/>
     <code> sudo apt-get install python2.7</code>
2. Install the Python development library <br/>
      <code>sudo apt-get install python-dev</code>
3. Install SIP <br/>
      <code>sudo apt-get install python-sip</code>
4. Install PyQt4 <br/>
      <code>sudo apt-get install python-qt4</code>
5. Install PyOpenGL <br/>
      <code>sudo apt-get install python-opengl</code>
6. Install numpy <br/>
     <code>sudo apt-get install python-numpy</code>
7. Install matplotlib <br/>
      <code>sudo apt-get install python-matplotlib</code>
8. Install Twisted <br/>
      <code>sudo apt-get install python-twisted</code>
9. Install git <br/>
      <code>sudo apt-get install git</code>
10. Clone the SLLURP repository <br/>
      <code>git clone https://github.com/ransford/sllurp.git</code>
11. Clone the WISP demo app repository <br/>
     <code>git clone https://github.com/zkapetanovic/RFID-Reader-GUI.git</code>

<h3>TROUBLESHOOTING</h3>

If you are unable to import sllurp, then you need to add the directory to your PYTHONPATH <br/>
      <code>export PYTHONPATH=$PYTHONPATH:YOUR/DIRECTORY/HERE/sllurp</code>

<h1>QUICK START</h1>
To get the demo started, follow these steps:

1. Open the terminal and cd into the directory of the WISP demo <br/>
      <code>cd YOUR/DIRECTORY/RFID-Reader-GUI</code>
2. Run main.py <br/>
      <code>python main.py</code>
3. When the application opens you need to configure the reader settings <br/>
      - Reader: Impinj
      - Modulation, Tari: WISP5, 7140
      - HOST IP: The IP of your reader
4. Once the reader settings have been selected, click the <b>CONNECT</b> button
5. Click the <b>START</b> button
6. At this point your reader should be connected and inventorying has started

<h2>DEMO FEATURES</h2>
With this application you can demo accelerometer and temperature data. Accelerometer data is demonstrated with the sliders under the Acceleromter tab and also with the Saturn Demo. Temperature data is displayed on a graph under the Temperature tab. 

<h3>SATURN DEMO CONFIGURATIONS</h3>
1. Click the Saturn tab
2. Click the Saturn button
3. Once the saturn demo opens, click the CALIBRATE button to set the proper orientation of Saturn.

<h3>MAKING MODIFICATIONS</h3>
- Additional reader settings can be found in <b>inventory.py</b>. All configurations can be modified in the readerConfig class.
- The <b>updateTagReport.py</b> module parses the EPCs and formats the sensor data
- The <b>GUI_Setup.py</b> module is where all widgets are initialized

<h2>CURRENT ISSUES TO BE AWARE OF</h2>
- Once an inventory has started the reader settings can no longer be changed. You must restart the application to make any changes.
- If you do not pause inventory before closing the application your reader will continue to run even though the application is closed
- If you close the saturn demo after opening it, the entire application will close as well
- If you enter the incorrect IP address and press start you will need to restart the application

