theme: /

    state: Помощь
        intent!: /помощь

        script:
            var result = callVoiceCommand("помощь");
            replyToUser(result.reply, $context);
