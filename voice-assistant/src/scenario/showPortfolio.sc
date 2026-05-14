theme: /

    state: ПоказатьПортфель
        intent!: /показать_портфель

        script:
            var result = callVoiceCommand("покажи портфель");
            replyToUser(result.reply, $context);
            sendPortfolioUpdate($context);
