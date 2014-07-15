%include('header.tpl', pretty=pretty)
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
                    <a href="{{ base_url }}{{ last_url }}">{{ base_url }}{{ last_url }}</a>
                    <a target="_blank" class="right" href="{{ base_url }}i/qr/{{ last_url }}">QR</a>
                </li>
            </ul>
        </div>
    %end
        <h2>New</h2>
        <form class="inputs" method="POST">
            %if last_error:
                <input autofocus class="input" type="text" name="url" id="url" placeholder="http://example.tld" value="{{ form_url }}">
                <input class="input" type="text" name="name" id="name" placeholder="cool_name (optional)" value="{{ form_name }}">
            %else:
                <input autofocus class="input" type="text" name="url" id="url" placeholder="http://example.tld">
                <input class="input" type="text" name="name" id="name" placeholder="cool_name (optional)">
            %end
            <button type="submit" class="input" id="submit">Create</button>
        </form>
%include('footer.tpl')