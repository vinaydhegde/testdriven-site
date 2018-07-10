---
layout: blog
title: William Vincent
permalink: authors/vincent
type: author
---

<hr><br>

<img src="/assets/img/authors/vincent.jpeg" style="max-width:200px;border-radius:50%" alt="william vincent">

William is a software developer and educator based in Boston. Formerly an early employee at [Quizlet](https://quizlet.com), he has taught computer science at [Williams College](https://www.williams.edu/) and is the author of two books: [Django for Beginners](https://www.amazon.com/Django-Beginners-Learn-web-development/dp/1980377898) and [REST APIs with Django](https://www.amazon.com/REST-APIs-Django-powerful-Python/dp/198302998X).

### Links

- [Twitter](https://twitter.com/wsv3000)
- [GitHub](https://github.com/wsvincent)
- [Personal Site](https://wsvincent.com/)

<div>
  <h3>Articles</h3>
  <ul>
    {% for post in site.posts %}
      {% if post.type == 'blog' and post.author == page.title %}
        <li><a href="{{site.url}}{{post.url}}">{{post.title}}</a></li>
      {% endif %}
    {% endfor %}
  </ul>
</div>
