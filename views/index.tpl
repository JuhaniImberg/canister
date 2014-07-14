<!DOCTYPE HTML>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=no">
    <title>canister</title>
    <link rel="stylesheet" type="text/css" href="/style">
</head>
<body>
    <div class="world">
    %if last_error:
        <h2>An error occured</h2>
        <div class="last">
            <ul>
                <li>
                    {{ last_error }}
                </li>
            </ul>
        </div>
    %end
    %if last_url:
        <h2>Your last link</h2>
        <div class="last">
            <ul>
                <li>
                    <a href="{{ last_url }}">{{ last_url }}</a>
                </li>
            </ul>
        </div>
    %end
        <h2>New</h2>
        <form class="inputs" method="POST">
            <input autofocus class="input" type="text" name="url" id="url" placeholder="http://example.tld">
            <input class="input" type="text" name="name" id="name" placeholder="cool_name (optional)">
            <button type="submit" class="input" id="submit">Create</button>
        </form>
    </div>
</body>
</html>