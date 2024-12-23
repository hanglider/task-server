#ifndef CLIENT_H
#define CLIENT_H

#include <QObject>
#include <QTcpServer>
#include <QTcpSocket>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QDir>

class Client : public QObject
{
    Q_OBJECT

public:
    explicit Client(QObject *parent = nullptr);
    void uploadFiles(const QString &filePath1, const QString &filePath2);
    void receiveFile();

signals:
    void uploadFinished(bool success);
    void fileReceived(bool success, const QString &filePath);

private slots:
    void onNewConnection();
    void onReadyRead(QTcpSocket *clientSocket);

private:
    QTcpServer *server;
    QString resultsDir;

    void sendResponse(QTcpSocket *clientSocket, int statusCode, const QString &message);
};

#endif // CLIENT_H
