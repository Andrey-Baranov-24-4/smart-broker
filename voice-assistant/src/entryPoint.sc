require: js/api.js
require: js/reply.js

require: scenario/addStock.sc
require: scenario/getPrice.sc
require: scenario/getProfit.sc
require: scenario/showPortfolio.sc
require: scenario/help.sc

patterns:
    $AnyText = $nonEmptyGarbage
    $OpenKeyWords = (включи|запусти|открой|давай)
    $ProjectName = (умный брокер|умного брокера|брокер)

theme: /

    state: Запуск
        q!: $regex</start>
        q!: [$repeat<$OpenKeyWords>] $ProjectName

        script:
            replyToUser(
                "Привет! Я Умный брокер. Могу добавить акцию, назвать цену или показать прибыль.",
                $context
            );
            sendPortfolioUpdate($context);

    state: Fallback
        event!: noMatch

        script:
            var text = $request.rawRequest.payload.message.original_text || "";
            if (text) {
                var result = callVoiceCommand(text);
                replyToUser(result.reply, $context);
            } else {
                var helpResult = callVoiceCommand("помощь");
                replyToUser(helpResult.reply, $context);
            }
