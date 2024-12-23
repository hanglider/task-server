#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QPushButton>
#include <QVBoxLayout>
#include <QLabel>
#include "client.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void onSelectFile1Clicked();
    void onSelectFile2Clicked();
    void onSendFilesClicked();
    void onUploadFinished(bool success);
    void onReceiveFileClicked();

private:
    QWidget *centralWidget;
    QVBoxLayout *layout;
    QPushButton *selectFile1Button;
    QPushButton *selectFile2Button;
    QPushButton *sendFilesButton;
    QPushButton *receiveFileButton;
    QLabel *file1Label;
    QLabel *file2Label;
    QLabel *statusLabel;

    QString filePath1;
    QString filePath2;
    Client *client;
};

#endif // MAINWINDOW_H
