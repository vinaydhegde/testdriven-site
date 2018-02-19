---
layout: blog
title: Jason Parent
permalink: authors/parent
type: author
---

<hr><br>

<img src="/assets/img/authors/parent.jpg" style="max-width:200px;border-radius:50%" alt="jason parent">

Jason is a full-stack web developer from Washington D.C with experience in Django and Angular. He's always seeking challenges and learning opportunities.

### Links

- [GitHub](https://github.com/ParentJA)
- [LinkedIn](https://www.linkedin.com/in/jason-parent-53b6341b/)

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
