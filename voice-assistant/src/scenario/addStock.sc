theme: /

    state: ДобавитьАкцию
        intent!: /добавить_акцию

        script:
            var text = $request.rawRequest.payload.message.original_text || "";
            var result = callVoiceCommand(text);
            replyToUser(result.reply, $context);
            sendPortfolioUpdate($context);

    state: ДобавитьАкциюFallback
        event!: addStock

        script:
            var text = $request.rawRequest.payload.message.original_text || "";
            var result = callVoiceCommand(text);
            replyToUser(result.reply, $context);
            sendPortfolioUpdate($context);
