import 'package:flutter/material.dart';
import 'package:flutter/painting.dart';
import 'package:flutter/painting.dart' as prefix0;
import 'package:flutter/services.dart';
import 'dart:math';
import 'dart:ui';
import 'dart:convert';
import 'package:web_socket_channel/io.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() => runApp(DashApp());

class DashApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    SystemChrome.setEnabledSystemUIOverlays(
        []); // Hide the status bar and nav-bar.
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Fantail Go Dashboard',
      theme: ThemeData(
          textTheme: Typography
              .englishLike2018, // Tell Flutter to use the 2018 material design spec for typography.
          primarySwatch: Colors.blue,
          backgroundColor: Colors
              .white // Sets the background to white, rather than a light grey.
          ),
      home: DashPage(),
    );
  }
}

class DashPage extends StatefulWidget {
  DashPage({Key key}) : super(key: key);

  @override
  DashState createState() => DashState();
}

class DashState extends State<DashPage> {
  String channelAddress = "ws://172.20.1.46:8765";
  WebSocketChannel channel =
      IOWebSocketChannel.connect("ws://172.20.1.46:8765");

  Map<String, Icon> iconTable = {
    "hot": Icon(Icons.whatshot, color: Colors.red, size: 36),
    "info": Icon(Icons.info, color: Colors.blue, size: 36)
  };

  Scaffold buildConnectingScreen(BuildContext context) {
    TextEditingController channelAddressInputController =
        TextEditingController();
    channelAddressInputController.text = channelAddress.replaceAll("ws://", "");
    return Scaffold(
      body: Column(
        children: <Widget>[
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                Padding(
                  padding: EdgeInsets.all(20),
                  child: CircularProgressIndicator(),
                ),
                Text("Connecting to Vehicle",
                    style: Theme.of(context).textTheme.title),
                Text("Ensure the Vehicle Elecontrics Unit is powered on."),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: <Widget>[
                Expanded(
                  child: TextField(
                    controller: channelAddressInputController,
                    decoration: InputDecoration(
                      labelText: 'IP Address + Port',
                    ),
                  ),
                ),
                OutlineButton(
                  child: Text("Go", style: Theme.of(context).textTheme.button),
                  onPressed: () {
                    channelAddress =
                        "ws://${channelAddressInputController.text}";
                    SystemChrome.setEnabledSystemUIOverlays(
                      []); // Hide the status bar and nav-bar.
                    setState(() {
                      channel = IOWebSocketChannel.connect(channelAddress);
                    });
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Scaffold buildDashScreen(String recievedData) {
    Map<String, dynamic> displayInfo = jsonDecode(
        recievedData); // Converts the recieved JSON string into a map.
    if (displayInfo['rearLidarScan'] == null) {
      displayInfo['rearLidarScan'] = 0;
    }
    return Scaffold(
      backgroundColor: Colors.white,
      body: Column(
        mainAxisSize: MainAxisSize.max,
        children: <Widget>[
          // Upper dash region.
          Container(
            height: 400,
            color: Color(0xFFFAFAFA),
            child: Row(
              children: <Widget>[
                Expanded(
                  child: Column(
                    children: <Widget>[
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.fromLTRB(16, 24, 16, 16),
                          child: Column(
                            children: <Widget>[
                              Padding(
                                padding: const EdgeInsets.only(bottom: 16),
                                child: Text("INFO",
                                    style: Theme.of(context).textTheme.caption),
                              ),
                              Expanded(
                                child: ListView.builder(
                                  shrinkWrap: true,
                                  itemCount: displayInfo['infoItems'].length ?? 0, // Not sure about this one...
                                  itemBuilder: (context, index) {
                                    ListTile tile;
                                    if (displayInfo['infoItems'][index]
                                        .containsKey('details')) {
                                      tile = ListTile(
                                        leading: iconTable[
                                            displayInfo['infoItems'][index]
                                                ['icon']],
                                        title: Text(displayInfo['infoItems']
                                            [index]['title']),
                                        subtitle: Text(displayInfo['infoItems']
                                            [index]['details']),
                                      );
                                    } else {
                                      tile = ListTile(
                                        leading: iconTable[
                                            displayInfo['infoItems'][index]
                                                ['icon']],
                                        title: Text(displayInfo['infoItems']
                                            [index]['title']),
                                      );
                                    }
                                    return Padding(
                                      padding: const EdgeInsets.only(bottom: 8),
                                      child: Card(
                                        elevation: 0,
                                        child: tile,
                                      ),
                                    );
                                  },
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.fromLTRB(24, 16, 16, 16),
                        child: Row(
                          children: <Widget>[
                            Visibility(
                              visible: displayInfo['phone'] ?? false,
                              child: Padding(
                                padding: const EdgeInsets.only(right: 16),
                                child: Icon(Icons.phonelink_ring,
                                    color: Colors.grey, size: 36),
                              ),
                            ),
                            Visibility(
                                visible: displayInfo['controller'] ?? false,
                                child: Icon(Icons.videogame_asset,
                                    color: Colors.grey, size: 36)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                // Drive Console
                Container(
                  width: 246,
                  child: Column(
                    children: <Widget>[
                      Padding(
                        padding: const EdgeInsets.all(8),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: <Widget>[
                            Text(
                              'R',
                              style: Theme.of(context)
                                  .textTheme
                                  .headline
                                  .copyWith(
                                      color: (displayInfo['mode'] == 2)
                                          ? Colors.lightBlueAccent
                                          : null,
                                      fontWeight: (displayInfo['mode'] == 2)
                                          ? FontWeight.bold
                                          : FontWeight.w300),
                            ),
                            Padding(
                              padding: const EdgeInsets.all(16),
                              child: Text(
                                'D',
                                style: Theme.of(context)
                                    .textTheme
                                    .headline
                                    .copyWith(
                                        color: (displayInfo['mode'] == 1)
                                            ? Colors.lightBlueAccent
                                            : null,
                                        fontWeight: (displayInfo['mode'] == 1)
                                            ? FontWeight.bold
                                            : FontWeight.w300),
                              ),
                            ),
                            Text(
                              'P',
                              style: Theme.of(context)
                                  .textTheme
                                  .headline
                                  .copyWith(
                                      color: (displayInfo['mode'] == 0)
                                          ? Colors.lightBlueAccent
                                          : null,
                                      fontWeight: (displayInfo['mode'] == 0)
                                          ? FontWeight.bold
                                          : FontWeight.w300),
                            ),
                          ],
                        ),
                      ),
                      Text((displayInfo['speed'] ?? 0).toInt().toString(),
                          style: Theme.of(context)
                              .textTheme
                              .display4
                              .copyWith(fontSize: 224)),
                      Text("km/h", style: Theme.of(context).textTheme.caption),
                    ],
                  ),
                ),

                Expanded(
                  child: Row(
                    mainAxisSize: MainAxisSize.max,
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: <Widget>[
                      // Power bars.
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: <Widget>[
                          Padding(
                            padding: EdgeInsets.only(right: 8),
                            child: Text("${((displayInfo['primaryBattery'] ?? 0) * 63).toStringAsFixed(2)}V", style: Theme.of(context).textTheme.caption),
                          ),
                          Container(
                            width: 20,
                            alignment: Alignment(1, 1),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.only(
                                  topLeft: Radius.circular(10)),
                              //color: Colors.white,
                            ),
                            height: 150,
                            child: FractionallySizedBox(
                              heightFactor:
                                  (displayInfo['primaryBattery'] ?? 0).toDouble(),
                              child: Container(
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.only(
                                      topLeft: Radius.circular(10)),
                                  color: Colors.green[400],
                                ),
                              ),
                            ),
                          ),
                          Container(
                            width: 20,
                            alignment: Alignment(1, -1),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.only(
                                  bottomLeft: Radius.circular(10)),
                              //color: Colors.white,
                            ),
                            height: 150,
                            child: FractionallySizedBox(
                              heightFactor:
                                  (displayInfo['secondaryBattery'] ?? 0).toDouble() * 2,
                              child: Container(
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.only(
                                      bottomLeft: Radius.circular(10)),
                                  color: Colors.blue[400],
                                ),
                              ),
                            ),
                          ),
                          Padding(
                            padding: EdgeInsets.only(right: 8),
                            child: Text("${((displayInfo['secondaryBattery'] ?? 0) * 60).toStringAsFixed(2)}V", style: Theme.of(context).textTheme.caption),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          Expanded(
            child: buildLidarSection(displayInfo),
          ),
        ],
      ),
    );
  }

  Widget buildLidarSection(Map<String, dynamic> displayInfo) {
    if (displayInfo['lidarScan'] != null) {
      return ClipRect(
        child: CustomPaint(
          painter: SurroundingsPainter(lidarScan: displayInfo['lidarScan']),
          child: Stack(
            children: <Widget>[
              Center(
                child: Container(
                  width: 100,
                  height: 200,
                  decoration: BoxDecoration(
                      color: Colors.grey[800],
                      borderRadius: BorderRadius.circular(10)),
                ),
              ),
              Center(
                child: Container(
                  decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey[300]),
                      borderRadius: BorderRadius.circular(80)),
                  width: 250,
                  height: 350,
                ),
              ),
              Center(
                child: Container(
                  decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey[300]),
                      borderRadius: BorderRadius.circular(160)),
                  width: 400,
                  height: 500,
                ),
              ),

              Visibility(
                visible: (displayInfo['rearLidarScan'] > 0) ? true : false,
                child: Positioned(
                  left: 300,
                  right: 300,
                  bottom: (((displayInfo['rearLidarScan'] ?? 0) * (-10 - 140)) / (2000)) + 140,
                  child: Container(
                    height: 75,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(10),
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter, // 10% of the width, so there are ten blinds.
                        colors: [const Color(0xFF50B9FF), const Color(0x00FFFFFF)], // whitish to gray
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    } else {
      return Center(
        child: Text("LiDAR Not Connected", style: Theme.of(context).textTheme.caption),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder(
        stream: channel.stream,
        builder: (context, snapshot) {
          switch (snapshot.connectionState) {
            case ConnectionState.waiting:
              return buildConnectingScreen(
                  context); // While we're waiting for a connection, show the waiting page.
            case ConnectionState.active:
              return buildDashScreen(
                  snapshot.data); // If the connection is active, show the dash.
            default:
              // If we don't have a connection yet, or the connection was closed: 1) Create a new connection, and 2) show the waiting page.
              channel = IOWebSocketChannel.connect(channelAddress);
              return buildConnectingScreen(context);
          }
        });
  }
}

class SurroundingsPainter extends CustomPainter {
  SurroundingsPainter({this.lidarScan});
  final List<dynamic> lidarScan;

  @override
  void paint(Canvas canvas, Size size) {
    final double scaleFactor = 12.05;

    Paint pointPaint = Paint();
    pointPaint.color = Color(0xFF50B9FF);
    pointPaint.strokeWidth = 5;
    pointPaint.strokeCap = StrokeCap.round;

    List<Offset> points = List<Offset>();

    // TODO: Work out what a Python tuple becomes after it's been through JSON.
    for (dynamic point in lidarScan) {
      points.add(
        Offset(
          size.width / 2 + (point[2] / scaleFactor) * sin(point[1] * (pi / 180.0)),
          size.height / 2 + 350 / scaleFactor - (point[2] / scaleFactor) * cos(point[1] * (pi / 180.0))
        )
      );
    }
    canvas.drawPoints(PointMode.points, points, pointPaint);

  }

  @override
  bool shouldRepaint(SurroundingsPainter oldDelegate) => true;
}


// Quality, Angle, Flattened Distance