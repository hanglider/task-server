#include "mainwindow.h"
#include <QPushButton>
#include <QVBoxLayout>
#include <QFileDialog>
#include <QLabel>
#include <QMessageBox>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent), client(new Client(this))
{
    // Центральный виджет и основной layout
    centralWidget = new QWidget(this);
    layout = new QVBoxLayout(centralWidget);

    // Кнопки для выбора и отправки файлов
    selectFile1Button = new QPushButton("Select File 1", this);
    selectFile2Button = new QPushButton("Select File 2", this);
    sendFilesButton = new QPushButton("Send Files", this);
    receiveFileButton = new QPushButton("Receive File", this);  // Кнопка для получения файла

    // Метки для отображения статуса и путей к файлам
    file1Label = new QLabel("File 1: Not selected", this);
    file2Label = new QLabel("File 2: Not selected", this);
    statusLabel = new QLabel("Status: Waiting for files", this);

    // Компоновка интерфейса
    layout->addWidget(selectFile1Button);
    layout->addWidget(file1Label);
    layout->addWidget(selectFile2Button);
    layout->addWidget(file2Label);
    layout->addWidget(sendFilesButton);
    layout->addWidget(receiveFileButton);  // Добавляем кнопку "Receive File"
    layout->addWidget(statusLabel);

    setCentralWidget(centralWidget);

    // Подключение сигналов и слотов
    connect(selectFile1Button, &QPushButton::clicked, this, &MainWindow::onSelectFile1Clicked);
    connect(selectFile2Button, &QPushButton::clicked, this, &MainWindow::onSelectFile2Clicked);
    connect(sendFilesButton, &QPushButton::clicked, this, &MainWindow::onSendFilesClicked);
    connect(receiveFileButton, &QPushButton::clicked, this, &MainWindow::onReceiveFileClicked);  // Подключаем слот для получения файла
    connect(client, &Client::uploadFinished, this, &MainWindow::onUploadFinished);
}

MainWindow::~MainWindow() {}

void MainWindow::onSelectFile1Clicked()
{
    filePath1 = QFileDialog::getOpenFileName(this, "Select File 1");
    if (!filePath1.isEmpty()) {
        file1Label->setText("File 1: " + filePath1);
    }
}

void MainWindow::onSelectFile2Clicked()
{
    filePath2 = QFileDialog::getOpenFileName(this, "Select File 2");
    if (!filePath2.isEmpty()) {
        file2Label->setText("File 2: " + filePath2);
    }
}

void MainWindow::onSendFilesClicked()
{
    if (filePath1.isEmpty() || filePath2.isEmpty()) {
        statusLabel->setText("Status: Please select both files before sending.");
        return;
    }

    statusLabel->setText("Status: Sending files...");
    client->uploadFiles(filePath1, filePath2);
}

void MainWindow::onUploadFinished(bool success)
{
    if (success) {
        statusLabel->setText("Status: Files uploaded successfully, waiting for results...");
    } else {
        statusLabel->setText("Status: Upload failed");
    }
}

void MainWindow::onReceiveFileClicked()
{
    statusLabel->setText("Status: Receiving file...");
    client->receiveFile();  // Вызов метода для получения файла от сервера
}
