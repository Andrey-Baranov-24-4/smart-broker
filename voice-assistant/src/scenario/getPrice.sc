theme: /

    state: ТекущаяЦена
        intent!: /текущая_цена

        script:
            var text = $request.rawRequest.payload.message.original_text || "";
            var result = callVoiceCommand(text);
            replyToUser(result.reply, $context);
