package jp.arkw.alpsrei.cp;

import android.app.AlertDialog;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.RemoteException;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.sunmi.peripheral.printer.InnerPrinterCallback;
import com.sunmi.peripheral.printer.InnerPrinterException;
import com.sunmi.peripheral.printer.InnerPrinterManager;
import com.sunmi.peripheral.printer.InnerResultCallback;
import com.sunmi.peripheral.printer.SunmiPrinterService;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Timer;
import java.util.TimerTask;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    private boolean isClock = false;
    private boolean isReceipt = false;
    private boolean permission = false;
    private String backend = "";
    private int id = -1;
    private Timer timer;
    private TimerTask timerTaskClock;
    private TimerTask timerTaskReceipt;
    private TaskClock taskClock;
    private TaskReceipt taskReceipt;
    private TextView textViewClock;
    private TextView textViewUrl;
    private TextView textViewVersion;

    private SunmiPrinterService sunmiPrinterService;
    public static int NoSunmiPrinter = 0x00000000;
    public static int CheckSunmiPrinter = 0x00000001;
    public static int FoundSunmiPrinter = 0x00000002;
    public static int LostSunmiPrinter = 0x00000003;
    public int sunmiPrinter = CheckSunmiPrinter;

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
        initSunmiPrinterService(this);
        findViewById(R.id.button_url).setOnClickListener(this);
        findViewById(R.id.button_card).setOnClickListener(this);
        textViewClock = findViewById(R.id.text_view_clock);
        textViewUrl = findViewById(R.id.text_view_url);
        textViewVersion = findViewById(R.id.text_view_version);
        textViewVersion.setText("Version " + getResources().getString(R.string.versionName));
        timer = new Timer();
        timerTaskClock = new TimerTask() {
            @Override
            public void run() {
                if (isClock == false && permission == true && backend.contains("http")) {
                    isClock = true;
                    taskClock = new TaskClock();
                    taskClock.execute(backend + "/clock");
                }
            }
        };
        timer.schedule(timerTaskClock, 0, 1000);
        timerTaskReceipt = new TimerTask() {
            @Override
            public void run() {
                if (isReceipt == false && permission == true && backend.contains("http")) {
                    isReceipt = true;
                    taskReceipt = new TaskReceipt();
                    taskReceipt.execute(backend + "/receipt");
                }
            }
        };
        timer.schedule(timerTaskReceipt, 0, 1000);
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
                                backend = editText.getText().toString();
                                textViewUrl.setText(backend + "/");
                                permission = true;
                            })
                    .setNegativeButton(
                            "キャンセル",
                            (dialog, which) -> {
                                permission = true;
                            })
                    .show();
        } else if (v.getId() == R.id.button_card) {
            printImage(BitmapFactory.decodeResource(getResources(), R.drawable.card));
            feedPaper(5);
        }
    }

    private String call(String uri) {
        HttpURLConnection httpURLConnection;
        InputStream inputStream;
        String result;
        String str = "";
        try {
            URL url = new URL(uri);
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

    private class TaskClock extends AsyncTask<String, Void, String> {
        protected String doInBackground(String... urls) {
            return call(urls[0]);
        }

        @Override
        protected void onPostExecute(String str_recv) {
            try {
                JSONObject jsonObject = new JSONObject(str_recv);
                textViewClock.setText(jsonObject.getString("clock"));
                isClock = false;
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }

    private class TaskReceipt extends AsyncTask<String, Void, String> {
        protected String doInBackground(String... urls) {
            return call(urls[0]);
        }

        @Override
        protected void onPostExecute(String str_recv) {
            try {
                JSONObject jsonObject = new JSONObject(str_recv);
                int nid = Integer.parseInt(jsonObject.getString("id"));
                if (id >= 0 && id != nid) {
                    printImage(BitmapFactory.decodeResource(getResources(), R.drawable.receipt1));
                    printText("COMIC BOX #0 / 海11\n", 0);
                    printImage(BitmapFactory.decodeResource(getResources(), R.drawable.receipt2));
                    printText("ご購入になりました商品の\n", 0);
                    printText("サポート情報はこちら ↓\n", 0);
                    printText("https://arkw.work/doujin\n", 0);
                    Date date = new Date();
                    SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy/MM/dd(E) HH:mm");
                    printText("レジ0001 " + simpleDateFormat.format(date) + "\n", 0);
                    printText("取" + String.format("%04d", nid) + " 責: 01 荒川\n\n", 0);
                    JSONArray items = jsonObject.getJSONArray("items");
                    for (int i = 0; i < items.length(); i++) {
                        JSONObject item = items.getJSONObject(i);
                        final int price = Integer.parseInt(item.getString("price"));
                        final int quantity = Integer.parseInt(item.getString("quantity"));
                        printText("" + item.getString("name") + " × " + quantity + "\n", 0);
                        final int subtotal = price * quantity;
                        printText("" + subtotal + "\n", 2);
                    }
                    printLine();
                    printDoubleText("合計", "￥ " + Integer.parseInt(jsonObject.getString("total")));
                    printDoubleText(jsonObject.getString("payment").replaceAll("\\r\\n|\\r|\\n", ""), "￥ " + Integer.parseInt(jsonObject.getString("cash")));
                    printDoubleText("お釣り", "￥ " + Integer.parseInt(jsonObject.getString("change")));
                    printLine();
                    printText("X/Twitter: @arkw0\n", 0);
                    printText("Misskey: @arkw@mi.arkw.work\n", 0);
                    printText("Website: https://arkw.net/\n", 0);
                    printText("E-mail: mail@arkw.net", 0);
                    feedPaper(5);
                }
                id = nid;
                isReceipt = false;
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }

    private void printText(String text, int alignment) {
        try {
            sunmiPrinterService.setAlignment(alignment, new InnerResultCallback() {
                @Override
                public void onRunResult(boolean isSuccess) throws RemoteException {
                }
                @Override
                public void onReturnString(String result) throws RemoteException {
                }
                @Override
                public void onRaiseException(int code, String msg) throws RemoteException {
                }
                @Override
                public void onPrintResult(int code, String msg) throws RemoteException {
                }
            });
        } catch (RemoteException e) {
            e.printStackTrace();
        };
        try {
            sunmiPrinterService.printText(text, new InnerResultCallback() {
                @Override
                public void onRunResult(boolean isSuccess) throws RemoteException {
                }
                @Override
                public void onReturnString(String result) throws RemoteException {
                }
                @Override
                public void onRaiseException(int code, String msg) throws RemoteException {
                }
                @Override
                public void onPrintResult(int code, String msg) throws RemoteException {
                }
            });
        } catch (RemoteException e) {
            e.printStackTrace();
        };
    }

    private void printDoubleText(String textLeft, String textRight) {
        try {
            sunmiPrinterService.printColumnsText(new String[]{textLeft, textRight}, new int[]{23, 8}, new int[]{0, 2}, new InnerResultCallback() {
                @Override
                public void onRunResult(boolean isSuccess) throws RemoteException {
                }
                @Override
                public void onReturnString(String result) throws RemoteException {
                }
                @Override
                public void onRaiseException(int code, String msg) throws RemoteException {
                }
                @Override
                public void onPrintResult(int code, String msg) throws RemoteException {
                }
            });
        } catch (RemoteException e) {
            e.printStackTrace();
        };
    }

    private void printImage(Bitmap bitmap) {
        try {
            sunmiPrinterService.printBitmap(bitmap, new InnerResultCallback() {
                @Override
                public void onRunResult(boolean isSuccess) throws RemoteException {
                }
                @Override
                public void onReturnString(String result) throws RemoteException {
                }
                @Override
                public void onRaiseException(int code, String msg) throws RemoteException {
                }
                @Override
                public void onPrintResult(int code, String msg) throws RemoteException {
                }
            });
        } catch (RemoteException e) {
            e.printStackTrace();
        };
    }

    private void printLine() {
        printText("--------------------------------\n", 1);
    }

    private void feedPaper(int n) {
        try {
            sunmiPrinterService.lineWrap(n, new InnerResultCallback() {
                @Override
                public void onRunResult(boolean isSuccess) throws RemoteException {
                }
                @Override
                public void onReturnString(String result) throws RemoteException {
                }
                @Override
                public void onRaiseException(int code, String msg) throws RemoteException {
                }
                @Override
                public void onPrintResult(int code, String msg) throws RemoteException {
                }
            });
        } catch (RemoteException e) {
            e.printStackTrace();
        };
    }

    private InnerPrinterCallback innerPrinterCallback = new InnerPrinterCallback() {
        @Override
        protected void onConnected(SunmiPrinterService service) {
            sunmiPrinterService = service;
            checkSunmiPrinterService(service);
        }
        @Override
        protected void onDisconnected() {
            sunmiPrinterService = null;
            sunmiPrinter = LostSunmiPrinter;
        }
    };

    private void checkSunmiPrinterService(SunmiPrinterService service) {
        boolean ret = false;
        try {
            ret = InnerPrinterManager.getInstance().hasPrinter(service);
        } catch (InnerPrinterException e) {
            e.printStackTrace();
        }
        sunmiPrinter = ret?FoundSunmiPrinter:NoSunmiPrinter;
    }

    public void initSunmiPrinterService(Context context) {
        try {
            boolean ret =  InnerPrinterManager.getInstance().bindService(context, innerPrinterCallback);
            if (!ret) {
                sunmiPrinter = NoSunmiPrinter;
            }
        } catch (InnerPrinterException e) {
            e.printStackTrace();
        }
    }
}