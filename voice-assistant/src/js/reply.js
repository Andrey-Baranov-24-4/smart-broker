// Вспомогательные функции для формирования ответа пользователю
// и отправки smart_app_data на Canvas App.

function replyToUser(text, context) {
    var body = {
        pronounceText: text,
        auto_listening: true,
        finished: false,
        emotion: { emotionId: "igrivost" },
        items: [{ bubble: { text: text, markdown: false } }]
    };
    context.response.replies = context.response.replies || [];
    context.response.replies.push({ type: "raw", body: body });
}

function sendPortfolioUpdate(context) {
    var command = { type: "smart_app_data", action: { action_id: "refresh_portfolio" } };
    context.response.replies = context.response.replies || [];
    context.response.replies.push({
        type: "raw",
        body: { items: [{ command: command }] }
    });
}
