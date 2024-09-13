package jp.arkw.alpsrei.cp;

import android.app.AlertDialog;
import android.os.AsyncTask;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Timer;
import java.util.TimerTask;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    private boolean running = false;
    private boolean permission = false;
    private String url = "";
    private Timer timer;
    private TimerTask timerTask;
    private Task task;
    private TextView textViewClock;
    private TextView textViewUrl;
    private TextView textViewVersion;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
        findViewById(R.id.button_url).setOnClickListener(this);
        textViewClock = findViewById(R.id.text_view_clock);
        textViewUrl = findViewById(R.id.text_view_url);
        textViewVersion = findViewById(R.id.text_view_version);
        textViewVersion.setText("Version " + getResources().getString(R.string.versionName));
        timer = new Timer();
        timerTask = new TimerTask() {
            @Override
            public void run() {
                if (running == false && permission == true && url.contains("http")) {
                    running = true;
                    task = new Task();
                    task.execute(url + "/clock");
                }
            }
        };
        timer.schedule(timerTask, 0, 1000);
        permission = true;
    }

    @Override
    public void onClick(View v) {
        if (v.getId() == R.id.button_url) {
            permission = false;
            LayoutInflater inflater = LayoutInflater.from(MainActivity.this);
            View view = inflater.inflate(R.layout.edit_dialog, null);
            final EditText editText = view.findViewById(R.id.edit_text);
            new AlertDialog.Builder(MainActivity.this)
                    .setTitle("バックエンドURLを入力 (例: http://192.168.0.1)")
                    .setView(view)
                    .setPositiveButton(
                            "OK",
                            (dialog, which) -> {
                                url = editText.getText().toString();
                                textViewUrl.setText(url + "/");
                                permission = true;
                            })
                    .setNegativeButton(
                            "キャンセル",
                            (dialog, which) -> {
                                permission = true;
                            })
                    .show();
        }
    }

    private class Task extends AsyncTask<String, Void, String> {
        protected String doInBackground(String... urls) {
            HttpURLConnection httpURLConnection;
            InputStream inputStream;
            String result;
            String str = "";
            try {
                URL url = new URL(urls[0]);
                httpURLConnection = (HttpURLConnection) url.openConnection();
                httpURLConnection.setConnectTimeout(10000);
                httpURLConnection.setReadTimeout(10000);
                httpURLConnection.setRequestMethod("GET");
                httpURLConnection.connect();
                int statusCode = httpURLConnection.getResponseCode();
                if (statusCode == 200){
                    inputStream = httpURLConnection.getInputStream();
                    BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream, "utf-8"));
                    result = bufferedReader.readLine();
                    while (result != null){
                        str += result;
                        result = bufferedReader.readLine();
                    }
                    bufferedReader.close();
                }
            } catch (MalformedURLException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
            return str;
        }

        @Override
        protected void onPostExecute(String str_recv) {
            try {
                JSONObject jsonObject = new JSONObject(str_recv);
                textViewClock.setText(jsonObject.getString("clock"));
                running = false;
            } catch (JSONException e) {
                e.printStackTrace();
            }
            return;
        }
    }
}