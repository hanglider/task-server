#include "client.h"
#include <QFileInfo>
#include <QRegularExpression>
#include <QStandardPaths>
#include <QFileDialog>
#include <QDebug>

Client::Client(QObject *parent)
    : QObject(parent), server(new QTcpServer(this))
{
    resultsDir = "client_results";
    QDir dir;
    if (!dir.exists(resultsDir)) {
        dir.mkpath(resultsDir);
    }

    connect(server, &QTcpServer::newConnection, this, &Client::onNewConnection);

    if (!server->listen(QHostAddress::Any, 5002)) {
        qCritical() << "Failed to start server on port 5002:" << server->errorString();
    } else {
        qDebug() << "HTTP server started, listening on port 5002";
    }
}

void Client::uploadFiles(const QString &filePath1, const QString &filePath2)
{
    QNetworkAccessManager *manager = new QNetworkAccessManager(this);

    QUrl url("http://192.168.3.12:8000/upload");
    QNetworkRequest request(url);

    QByteArray boundary = "------------------------boundary";
    request.setHeader(QNetworkRequest::ContentTypeHeader, "multipart/form-data; boundary=" + boundary);

    QByteArray body;
    auto appendFile = [&](const QString &filePath, const QString &fieldName) {
        QFile file(filePath);
        if (file.open(QIODevice::ReadOnly)) {
            body.append("--" + boundary + "\r\n");
            body.append("Content-Disposition: form-data; name=\"" + fieldName + "\"; filename=\"" + QFileInfo(file).fileName() + "\"\r\n");
            body.append("Content-Type: application/octet-stream\r\n\r\n");
            body.append(file.readAll());
            body.append("\r\n");
            file.close();
        }
    };

    appendFile(filePath1, "file1");
    appendFile(filePath2, "file2");
    body.append("--" + boundary + "--\r\n");

    QNetworkReply *reply = manager->post(request, body);
    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        if (reply->error() == QNetworkReply::NoError) {
            emit uploadFinished(true);
        } else {
            emit uploadFinished(false);
            qDebug() << "Upload error:" << reply->errorString();
        }
        reply->deleteLater();
    });
}

void Client::receiveFile()
{
    qDebug() << "Waiting for incoming files...";
}

void Client::onNewConnection()
{
    QTcpSocket *clientSocket = server->nextPendingConnection();
    connect(clientSocket, &QTcpSocket::readyRead, this, [this, clientSocket]() {
        onReadyRead(clientSocket);
    });
    connect(clientSocket, &QTcpSocket::disconnected, clientSocket, &QTcpSocket::deleteLater);
}

void Client::onReadyRead(QTcpSocket *clientSocket)
{
    QByteArray request = clientSocket->readAll();
    QString requestString = QString::fromUtf8(request);

    if (!requestString.startsWith("POST /receive_results")) {
        sendResponse(clientSocket, 404, "Not Found");
        return;
    }

    QRegularExpression re("Content-Disposition:.*filename=\"([^\"]+)\"");
    QRegularExpressionMatch match = re.match(requestString);
    if (!match.hasMatch()) {
        sendResponse(clientSocket, 400, "Bad Request");
        return;
    }
    QString fileName = match.captured(1);

    int contentIndex = request.indexOf("\r\n\r\n");
    if (contentIndex == -1) {
        sendResponse(clientSocket, 400, "Bad Request");
        return;
    }
    QByteArray fileData = request.mid(contentIndex + 4);

    QString filePath = QFileDialog::getSaveFileName(nullptr, "Save File", fileName);
    if (filePath.isEmpty()) {
        sendResponse(clientSocket, 400, "Save Path Not Selected");
        return;
    }

    QFile file(filePath);
    if (!file.open(QIODevice::WriteOnly)) {
        sendResponse(clientSocket, 500, "Internal Server Error");
        return;
    }
    file.write(fileData);
    file.close();

    qDebug() << "File received successfully:" << filePath;
    sendResponse(clientSocket, 200, "File received successfully");
    emit fileReceived(true, filePath);
}

void Client::sendResponse(QTcpSocket *clientSocket, int statusCode, const QString &message)
{
    QString response = QString("HTTP/1.1 %1 %2\r\n"
                               "Content-Type: text/plain\r\n"
                               "Content-Length: %3\r\n"
                               "\r\n"
                               "%4")
                           .arg(statusCode)
                           .arg(statusCode == 200 ? "OK" : "Error")
                           .arg(message.size())
                           .arg(message);

    clientSocket->write(response.toUtf8());
    clientSocket->flush();
    clientSocket->disconnectFromHost();
}
