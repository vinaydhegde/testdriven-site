---
layout: blog
title: Pete Jeffryes
permalink: authors/jeffryes
type: author
---

<hr><br>

<img src="/assets/img/authors/jeffryes.jpeg" style="max-width:200px;border-radius:50%" alt="pete jeffryes">

Pete a software developer who loves to build tools. He has a lot of experience with language learning: music, Mandarin Chinese, and code. He is fascinated by patterns/systems and their manipulation.

### Links

- [GitHub](https://github.com/topleft)
- [LinkedIn](https://www.linkedin.com/in/topleft/)

<div>
  <h3>Articles</h3>
  {% for post in site.posts %}
    <ul>
      {% if post.type == 'blog' and post.author == page.title %}
        <li><a href="{{site.url}}{{post.url}}">{{post.title}}</a></li>
      {% endif %}
    </ul>
  {% endfor %}
</div>
