<center> <table border=1>
    <tr>
        <th>Title</th>
        <th>Author</th>
        <th>#likes</th>
        <th>#comments</th>
        <th colspan="3">Label</th>
    </tr>
    %for row in rows:
        <tr bgcolor = {{row[1]}}>
            <td><a href="{{row[2].url}}">{{row[2].title}}</a></td>
            <td>{{row[2].author}}</td>
            <td>{{row[2].points}}</td>
            <td>{{row[2].comments}}</td>
             <td><a href="/add_label/?label=good&id={{row[2].id}}">Интересно</a></td>
            <td><a href="/add_label/?label=maybe&id={{row[2].id}}">Возможно</a></td>
            <td><a href="/add_label/?label=never&id={{row[2].id}}">Не интересно</a></td>
        </tr>
    %end
</table>
<br>
<a href="/update_news">I Wanna More HACKER NEWS!</a></center>