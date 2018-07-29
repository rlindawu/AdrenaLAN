// Copyright 2018 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package edmt.dev.androidcamera2api;

import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.os.Environment;

import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

import java.io.File;
import java.util.List;
import java.util.UUID;

/** Graphic instance for rendering image labels. */
//File globalFile;
public class myJavaClass {


  public String myMethod(double lat, double lon) {
//        LocationManager lm = (LocationManager)getSystemService(Context.LOCATION_SERVICE);
//        Location location = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER);
//        double longitude = location.getLongitude();
//        double latitude = location.getLatitude();


    PythonInterpreter interpreter = new PythonInterpreter();
    interpreter.execfile("\\Users\\Linda\\Documents\\U of T Engineering\\2017\\AdrenaLAN\\imagenet\\adrenalan\\query_nearby.py");

    //interpreter.set("latitude", 43.7033);
    //interpreter.set("longitude", -79.6377);
      interpreter.set("latitude", lat);
      interpreter.set("longitude", lon);
    interpreter.set("img_input", Environment.getExternalStorageDirectory()+"/"+ UUID.randomUUID().toString()+".jpg");
    PyObject result = interpreter.eval("process_wrapper(latitude, longitude, img_input)");
    String javaResult = result.toString();
    return javaResult;
    //System.out.println(result.toString());

  }
}