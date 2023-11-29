import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineCore import QWebEngineCookieStore

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.chess.com/play/online")) 
        self.setCentralWidget(self.browser)
        self.setWindowTitle("chess AI")
        self.resize(1920, 1080)
        self.setGeometry(100, 100, 1080, 600)
        navtb = QToolBar("Навигация")
        self.addToolBar(navtb)
        back_btn = QAction("Назад", self)
        back_btn.setStatusTip("Назад на предыдущую страницу")
        back_btn.triggered.connect(self.browser.back)
        navtb.addAction(back_btn)
        next_btn = QAction("Вперед", self)
        next_btn.setStatusTip("Перейти на следующую страницу")
        next_btn.triggered.connect(self.browser.forward)
        navtb.addAction(next_btn)
        reload_btn = QAction("Обновить", self)
        reload_btn.setStatusTip("Обновить страницу")
        reload_btn.triggered.connect(self.browser.reload)
        navtb.addAction(reload_btn)
        home_btn = QAction("Домой", self)
        home_btn.setStatusTip("Перейти на домашнюю страницу")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)
        navtb.addSeparator()
        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)
        stop_btn = QAction("Стоп", self)
        stop_btn.setStatusTip("Остановить загрузку страницы")
        stop_btn.triggered.connect(self.browser.stop)
        navtb.addAction(stop_btn)
        self.browser.urlChanged.connect(self.update_urlbar)
        self.start_button = QPushButton("Start", self)
        self.start_button.setStatusTip("Запустить JavaScript-скрипт")
        self.start_button.clicked.connect(self.run_js_script)
        navtb.addWidget(self.start_button)
        self.page_loaded = False
        self.browser.loadFinished.connect(self.on_load_finished)

    def navigate_home(self):
        self.browser.setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.browser.setUrl(q)

    def update_urlbar(self, q):
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def on_load_finished(self, ok):
        if ok:
            self.page_loaded = True
            self.start_button.setEnabled(True)  # разреш.
            #self.page_loaded = False
            #self.start_button.setEnabled(False)  # запрет

    def run_js_script(self):
        if self.page_loaded:
            # JavaScript-код, который будет выполнен при нажатии кнопки sta rt 
            js_code = """
            function main() {
    let chessboard = document.querySelector("wc-chess-board");
    if (chessboard == null || !chessboard) {
        return { status: "false", error: "Не удаётся запустить скрипт. Пожалуйста, делайте это тогда в самой игре" };
    }

    var player_colour = 'white';
    player_colour = prompt("Ты играешь за white или black ?");
    while (player_colour !== "white" && player_colour !== "black") {
        player_colour = prompt("Ты играешь за white или black ?");
    }
    player_colour = player_colour.charAt(0);

    function getFenString() {
        let fen_string = "";
        for (let i = 8; i >= 1; i--) {
            for (let j = 1; j <= 8; j++) {
                let position = `${j}${i}`;
                if (j === 1 && i !== 8) {
                    fen_string += "/";
                }

                let piece_in_position = document.querySelectorAll(`.piece.square-${position}`)[0]?.classList ?? null;

                if (piece_in_position !== null) {
                    for (let item of piece_in_position.values()) {
                        if (item.length === 2) {
                            piece_in_position = item;
                        }
                    }
                }

                if (piece_in_position === null) {
                    let previous_char = fen_string.split("").pop();
                    if (!isNaN(Number(previous_char))) {
                        fen_string = fen_string.substring(0, fen_string.length - 1);
                        fen_string += Number(previous_char) + 1;
                    } else {
                        fen_string += "1";
                    }
                } else if (piece_in_position?.split("")[0] === "b") {
                    fen_string += piece_in_position.split("")[1];
                } else if (piece_in_position?.split("")[0] === "w") {
                    fen_string += piece_in_position.split("")[1].toUpperCase();
                }
            }
        }
        return fen_string;
    }

    let fen_string = getFenString();
    fen_string += ` ${player_colour}`;
    console.log(fen_string);

    const engine = new Worker("/bundles/app/js/vendor/jschessengine/stockfish.asm.1abfa10c.js");
    engine.postMessage(`position fen ${fen_string}`);
    engine.postMessage('go wtime 300000 btime 300000 winc 2000 binc 2000');
    engine.postMessage("go debth 99");

    setInterval(() => {
        let new_fen_string = getFenString();
        new_fen_string += ` ${player_colour}`;
        if (new_fen_string !== fen_string) {
            fen_string = new_fen_string;
            engine.postMessage(`position fen ${fen_string}`);
            engine.postMessage('go wtime 300000 btime 300000 winc 2000 binc 2000');
            engine.postMessage("go debth 99");
        }
    });

    engine.onmessage = function (event) {
        if (event.data.startsWith('bestmove')) {
            const bestMove = event.data.split(' ')[1];
            const char_map = { "a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8 };
            document.getElementById("best-move").innerHTML = ` Лучший ход это ${bestMove}`;

            document.querySelectorAll(".cheat-highlight").forEach((element) => {
                element.remove();
            });

            const bestMoveArray = bestMove.split("");
            const initialPosition = `${char_map[bestMoveArray[0]]}${bestMoveArray[1]}`;
            const finalPosition = `${char_map[bestMoveArray[2]]}${bestMoveArray[3]}`;

            const initialHighlight = document.createElement("div");
            initialHighlight.className = `highlight cheat-highlight square-${initialPosition}`;
            initialHighlight.style.background = "blue";
            initialHighlight.style.opacity = 0.2;
            initialHighlight.style.border = "5px outset white";
            initialHighlight.style.color = "white";
            initialHighlight.innerHTML = "";

            const finalHighlight = document.createElement("div");
            finalHighlight.className = `highlight cheat-highlight square-${finalPosition}`;
            finalHighlight.style.background = "red";
            finalHighlight.style.opacity = 0.3;
            finalHighlight.style.border = "5px outset white";
            finalHighlight.style.color = "white";
            finalHighlight.innerHTML = "";

            chessboard.appendChild(initialHighlight);
            chessboard.appendChild(finalHighlight);
        }
    };

    return { status: true };
}

function startHack(element) {
    element.innerHTML = "Пожалуйста подождите..";
    element.disabled = true;
    let hack = main();
    if (hack.status === true) {
        element.innerHTML = `<span id='best-move'>Рассчёт лучшего хода..</span>`;
    } else {
        element.innerHTML = "Start Hack";
        element.disabled = false;
        alert(hack.error);
    }
}

var button = document.createElement("button");
button.className = "ui_v5-button-full";
button.innerHTML = "Запустить";
button.onclick = () => { startHack(button); };
let main_body = document.querySelector(".board-layout-main");
main_body.prepend(button);
"""
            self.browser.page().runJavaScript(js_code)
        else:
            QMessageBox.warning(self, "Предупреждение", "Дождитесь полной загрузки страницы перед выполнением скрипта.")

app = QApplication(sys.argv)
QApplication.setApplicationName("browser")
window = Browser()
window.show()
app.exec_()
