theme: /

    state: МояПрибыль
        intent!: /моя_прибыль

        script:
            var text = $request.rawRequest.payload.message.original_text || "";
            var result = callVoiceCommand(text);
            replyToUser(result.reply, $context);
