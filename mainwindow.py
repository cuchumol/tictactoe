from PyQt6.QtCore import Qt, QPointF, QPoint, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget, QMainWindow, QTableWidget,  QHeaderView, QAbstractScrollArea, QVBoxLayout, QPushButton, QMessageBox
from PyQt6.QtGui import QPainter, QPen

from minimax import TicTacToe, check_winner


game_board = TicTacToe()


class PaintWidget(QWidget):
    computer_move_signal = pyqtSignal(int)
    end_game_signal = pyqtSignal(str)
    next_paint_zero_zero_signal = pyqtSignal(bool)

    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(10, 10)
        self.margin = 15  # Отступ от границ виджета
        
        self.should_paint_cross = False
        self.should_paint_zero = False
        self.should_trigger = True

        self.game_mode = 1 # 1 - computer, 2 - users

        self.next_paint_zero = False


    def set_paint_mode(self, mode):
        self.next_paint_zero = mode

    def set_game_mode(self, game_mode):
        self.game_mode = game_mode


    def clearHost(self):
        self.should_paint_cross = False
        self.should_paint_zero = False
        self.should_trigger = True
      #  game_board.clear_board()
        self.update()

        

    def paintZero(self):
        if self.should_trigger:
            self.should_paint_zero = True
            self.should_trigger = False
            
            self.update()
    


    def paintEvent(self, event):
        if self.should_paint_cross == True:
            painter = QPainter(self)

            width = self.size().width()
            height = self.size().height()

            painter.setPen(QPen(Qt.GlobalColor.red, 4, Qt.PenStyle.SolidLine))
        

            painter.drawLine(QPointF(self.margin, self.margin), QPointF(width - self.margin, height - self.margin))
            painter.drawLine(QPointF(width - self.margin, self.margin), QPointF(self.margin, height - self.margin))

        
        elif self.should_paint_zero == True:
            painter = QPainter(self)

            width = self.size().width()
            height = self.size().height()
            
            radius = min(width, height) // 3
            center = QPoint(width // 2, height // 2)
            
            painter.setPen(QPen(Qt.GlobalColor.green, 4, Qt.PenStyle.SolidLine))
            painter.drawEllipse(center, radius, radius)

    
    def blockHost(self):
        self.should_trigger = False

    
    def mousePressEvent(self, event):
        if self.should_trigger and event.button() == Qt.MouseButton.LeftButton:
            widget_pos = self.mapToGlobal(event.position().toPoint())
            table_widget = self.parentWidget().parentWidget()
            table_pos = table_widget.mapFromGlobal(widget_pos)

            row = table_widget.rowAt(table_pos.y())
            column = table_widget.columnAt(table_pos.x())
                

            if self.game_mode == 1:

                self.should_paint_cross = True
                self.should_trigger = False

                self.update()
                
                # index=row×number_of_columns+column
                game_board.user_move(row*3 + column, 'X')

                winner = check_winner(game_board.board)
                if winner is not None:
                    self.end_game_signal.emit(winner)
                elif ' ' not in game_board.board:
                    self.end_game_signal.emit('D')
                else:
                    computer_move = game_board.computer_move()
                    self.computer_move_signal.emit(computer_move)
            else:
                
                if not self.next_paint_zero:
                    self.should_paint_cross = True
                    self.should_trigger = False
                    game_board.user_move(row*3 + column, 'X')

                    self.next_paint_zero_zero_signal.emit(True)

                else:
                    self.should_paint_zero = True
                    self.should_trigger = False
                    game_board.user_move(row*3 + column, 'O')


                    self.next_paint_zero_zero_signal.emit(False)


                self.update()


                

                
                # index=row×number_of_columns+column

                winner = check_winner(game_board.board)
                if winner is not None:
                    self.end_game_signal.emit(winner)
                elif ' ' not in game_board.board:
                    self.end_game_signal.emit('D')



    



class MainWindow(QMainWindow):
    def __init__(self, parent=None, flags=Qt.WindowType.Window) -> None:
        super().__init__(parent, flags)
        
        self.setWindowTitle("Tic tac toe")

        self.resize(400, 300)


        self.table_widget = QTableWidget(3, 3)
        
        self.table_widget.horizontalHeader().setVisible(False)
        self.table_widget.verticalHeader().setVisible(False)
        

        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)


        for i in range(3):
            for j in range(3):
                paintwidget = PaintWidget()
                paintwidget.computer_move_signal.connect(self.get_computer_move)
                paintwidget.end_game_signal.connect(self.get_winner_info)
                paintwidget.next_paint_zero_zero_signal.connect(self.set_paint_mode)
                self.table_widget.setCellWidget(i, j, paintwidget)


        self.btn1 = QPushButton('Computer game')
        self.btn2 = QPushButton('Game with another user')
        
        self.set_btn_style(self.btn1, True)
        self.set_btn_style(self.btn2, False)

        self.active_btn = 1
        
        self.btn3 = QPushButton('Restart')


        container = QWidget(self)

        central_layout = QVBoxLayout(container)
        central_layout.addWidget(self.table_widget)
        central_layout.addWidget(self.btn1)
        central_layout.addWidget(self.btn2)
        central_layout.addWidget(self.btn3)


        self.setCentralWidget(container)


        self.btn1.clicked.connect(self.activate_btn1)
        self.btn2.clicked.connect(self.activate_btn2)
        self.btn3.clicked.connect(self.clear_board)

        # signals


    @pyqtSlot(bool)
    def set_paint_mode(self, mode):
        for i in range(3):
            for j in range(3):
                 self.table_widget.cellWidget(i, j).set_paint_mode(mode)




    @pyqtSlot(int)
    def get_computer_move(self, coord):
        computer_row = coord // 3
        computer_col = coord % 3

        self.table_widget.cellWidget(computer_row, computer_col).paintZero()

        winner = check_winner(game_board.board)
        if winner is not None:
            self.get_winner_info(winner)
        elif ' ' not in game_board.board:
            self.get_winner_info('D')


    @pyqtSlot(str)
    def get_winner_info(self, winner):
        for i in range(3):
            for j in range(3):
                 self.table_widget.cellWidget(i, j).blockHost()
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle('End game')
        if winner == 'D':
            msg_box.setText('Dead heat')
        else:
            msg_box.setText(f'Winner: {winner}')
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()



    def set_btn_style(self, button, active):
        if active:
            # btn1.setStyleSheet("border: 2px solid lightgray;")
            button.setStyleSheet("border: 2px solid green;")
        else:
            button.setStyleSheet("")



    @pyqtSlot()
    def activate_btn1(self):
        self.set_btn_style(self.btn1, True)
        self.set_btn_style(self.btn2, False)
        game_board.clear_board()


        for i in range(3):
            for j in range(3):
                self.table_widget.cellWidget(i, j).clearHost()
                self.table_widget.cellWidget(i, j).set_game_mode(1)

       # if self.active_btn != 1:
        
        #self.active_btn = 1


    @pyqtSlot()
    def activate_btn2(self):
        self.set_btn_style(self.btn2, True)
        self.set_btn_style(self.btn1, False)
        game_board.clear_board()

        for i in range(3):
            for j in range(3):
                self.table_widget.cellWidget(i, j).clearHost()
                self.table_widget.cellWidget(i, j).set_game_mode(2)
    
    @pyqtSlot()
    def clear_board(self):
        game_board.clear_board()
        for i in range(3):
            for j in range(3):
                 self.table_widget.cellWidget(i, j).clearHost()
                 self.table_widget.cellWidget(i, j).set_paint_mode(False)


