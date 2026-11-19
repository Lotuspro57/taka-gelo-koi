package app.takagelokoi

import android.app.Activity
import android.content.ContentValues
import android.content.Intent
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.view.View
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.core.content.FileProvider
import org.json.JSONObject
import java.io.File

/**
 * "টাকা গেল কই?" — a thin native shell around the single-file web app in
 * assets/index.html. The web app talks to this class through `window.AndroidBridge`.
 *
 * Bridge methods (all called from web/index.html):
 *   setTheme(dark)               status/navigation bar colours
 *   saveBackup(json, filename)   write a backup into Downloads
 *   shareBackup(json, filename)  share a backup via WhatsApp / Telegram / mail …
 *   openFilePicker()             pick a backup .json  -> window.onImportDataReceived(text)
 *   checkForUpdate()             pick a new index.html -> stored, then window.onUpdateCheckResult(true, name)
 *   applyUpdate()                reload using the stored update file
 */
class MainActivity : Activity() {

    private lateinit var web: WebView
    private var pendingBackup: String? = null
    private val updateFile by lazy { File(filesDir, "update.html") }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        dropStaleUpdate()

        web = WebView(this)
        setContentView(web)
        applyBars(false)

        web.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true   // localStorage = all of the user's data
            allowFileAccess = true
            allowContentAccess = true
            setSupportZoom(false)
        }
        web.webChromeClient = WebChromeClient()
        web.webViewClient = WebViewClient()
        web.addJavascriptInterface(Bridge(), "AndroidBridge")
        loadApp()
    }

    /** A freshly installed APK always wins over an older side-loaded update file. */
    private fun dropStaleUpdate() {
        if (!updateFile.exists()) return
        try {
            val installed = packageManager.getPackageInfo(packageName, 0).lastUpdateTime
            if (updateFile.lastModified() < installed) updateFile.delete()
        } catch (e: Exception) {
        }
    }

    private fun bundledHtml(): String =
        assets.open("index.html").bufferedReader(Charsets.UTF_8).use { it.readText() }

    private fun loadApp() {
        val html = try {
            if (updateFile.exists() && updateFile.length() > 0) updateFile.readText(Charsets.UTF_8) else bundledHtml()
        } catch (e: Exception) {
            bundledHtml()
        }
        // A fixed file:// base URL keeps localStorage in the same place for the bundled
        // page and for any side-loaded update, so data is never lost on update.
        web.loadDataWithBaseURL("file:///android_asset/", html, "text/html", "UTF-8", null)
    }

    private fun applyBars(dark: Boolean) {
        val c = Color.parseColor(if (dark) "#111915" else "#FBF7EE")
        window.statusBarColor = c
        window.navigationBarColor = c
        var f = window.decorView.systemUiVisibility
        val lightStatus = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
        val lightNav = if (Build.VERSION.SDK_INT >= 26) View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR else 0
        f = if (dark) f and (lightStatus or lightNav).inv() else f or lightStatus or lightNav
        window.decorView.systemUiVisibility = f
    }

    private fun js(code: String) = runOnUiThread { web.evaluateJavascript(code, null) }
    private fun toast(msg: String) = runOnUiThread { Toast.makeText(this, msg, Toast.LENGTH_LONG).show() }

    private fun pickFile(req: Int) {
        val i = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "*/*"
        }
        try {
            startActivityForResult(i, req)
        } catch (e: Exception) {
            toast("ফাইল বাছাই খোলা যাচ্ছে না")
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (resultCode != RESULT_OK) return
        val uri = data?.data ?: return

        if (requestCode == REQ_SAVE) { // Android 9 and older: user chose where to save
            val json = pendingBackup
            pendingBackup = null
            val ok = try {
                contentResolver.openOutputStream(uri)?.use { it.write((json ?: "").toByteArray(Charsets.UTF_8)) }
                true
            } catch (e: Exception) {
                false
            }
            js("window.onBackupSaved($ok, '')")
            return
        }

        val text = try {
            contentResolver.openInputStream(uri)?.bufferedReader(Charsets.UTF_8)?.use { it.readText() }
        } catch (e: Exception) {
            null
        }
        if (text == null) {
            toast("ফাইলটি পড়া যায়নি")
            return
        }
        when (requestCode) {
            REQ_IMPORT -> js("window.onImportDataReceived(${JSONObject.quote(text)})")
            REQ_UPDATE -> {
                if (!text.contains("<html", ignoreCase = true) || !text.contains("AndroidBridge")) {
                    js("window.onUpdateCheckResult(false, ${JSONObject.quote("এটি সঠিক অ্যাপ ফাইল নয়")})")
                    return
                }
                try {
                    updateFile.writeText(text, Charsets.UTF_8)
                    js("window.onUpdateCheckResult(true, '')")
                } catch (e: Exception) {
                    js("window.onUpdateCheckResult(false, ${JSONObject.quote("আপডেট ফাইল সেভ করা যায়নি")})")
                }
            }
        }
    }

    /** Android 10+: write straight into Downloads, no permission needed. Returns a label or null. */
    private fun saveToDownloads(json: String, name: String): String? = try {
        val v = ContentValues().apply {
            put(MediaStore.Downloads.DISPLAY_NAME, name)
            put(MediaStore.Downloads.MIME_TYPE, "application/json")
            put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS)
        }
        val uri = contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v)!!
        contentResolver.openOutputStream(uri)!!.use { it.write(json.toByteArray(Charsets.UTF_8)) }
        "Downloads/$name"
    } catch (e: Exception) {
        null
    }

    private fun shareJson(json: String, name: String) {
        try {
            val dir = File(cacheDir, "backups").apply { mkdirs() }
            val f = File(dir, name).apply { writeText(json, Charsets.UTF_8) }
            val uri = FileProvider.getUriForFile(this, "$packageName.files", f)
            val i = Intent(Intent.ACTION_SEND).apply {
                type = "application/json"
                putExtra(Intent.EXTRA_STREAM, uri)
                putExtra(Intent.EXTRA_SUBJECT, "টাকা গেল কই? ব্যাকআপ")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(i, "ব্যাকআপ পাঠান"))
        } catch (e: Exception) {
            toast("পাঠানো যায়নি")
        }
    }

    inner class Bridge {
        @JavascriptInterface
        fun setTheme(dark: Boolean) = runOnUiThread { applyBars(dark) }

        @JavascriptInterface
        fun checkForUpdate() = runOnUiThread { pickFile(REQ_UPDATE) }

        @JavascriptInterface
        fun openFilePicker() = runOnUiThread { pickFile(REQ_IMPORT) }

        @JavascriptInterface
        fun applyUpdate() = runOnUiThread {
            if (updateFile.exists()) loadApp() else toast("আগে আপডেট ফাইল বেছে নিন")
        }

        @JavascriptInterface
        fun saveBackup(json: String, filename: String) {
            if (Build.VERSION.SDK_INT >= 29) {
                val where = saveToDownloads(json, filename)
                js("window.onBackupSaved(${where != null}, ${JSONObject.quote(where ?: "")})")
            } else {
                pendingBackup = json
                runOnUiThread {
                    val i = Intent(Intent.ACTION_CREATE_DOCUMENT).apply {
                        addCategory(Intent.CATEGORY_OPENABLE)
                        type = "application/json"
                        putExtra(Intent.EXTRA_TITLE, filename)
                    }
                    try {
                        startActivityForResult(i, REQ_SAVE)
                    } catch (e: Exception) {
                        js("window.onBackupSaved(false, '')")
                    }
                }
            }
        }

        @JavascriptInterface
        fun shareBackup(json: String, filename: String) = runOnUiThread { shareJson(json, filename) }
    }

    /** Lets the web app close its own sheets/screens first; only exits from the home screen. */
    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        web.evaluateJavascript("(function(){return !!(window.handleBack&&window.handleBack());})()") { r ->
            if (r != "true") super@MainActivity.onBackPressed()
        }
    }

    override fun onResume() {
        super.onResume()
        web.onResume()
    }

    override fun onPause() {
        web.onPause()
        super.onPause()
    }

    override fun onDestroy() {
        web.destroy()
        super.onDestroy()
    }

    companion object {
        private const val REQ_IMPORT = 101
        private const val REQ_UPDATE = 102
        private const val REQ_SAVE = 103
    }
}
