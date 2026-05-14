// Вызов FastAPI backend /voice/command.
// BACKEND_URL задаётся в переменных среды SmartApp Studio.
var BACKEND_URL = typeof $env !== "undefined" && $env.BACKEND_URL
    ? $env.BACKEND_URL
    : "https://212-8-227-28.sslip.io";

function callVoiceCommand(text) {
    try {
        var response = $http.post(BACKEND_URL + "/voice/command", {
            headers: {
                "Content-Type": "application/json; charset=utf-8",
                "ngrok-skip-browser-warning": "true"
            },
            body: { text: text },
            dataType: "json",
            timeout: 20000
        });
        if (response && response.status === 200) {
            return typeof response.data === "string"
                ? JSON.parse(response.data)
                : response.data;
        }
        var detail = response && (response.status + " " + (response.statusText || ""));
        return { reply: "Ошибка сервера: " + detail };
    } catch (e) {
        return { reply: "Не удалось соединиться с сервером: " + e };
    }
}
