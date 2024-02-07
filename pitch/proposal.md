# Capstone Project 1 Proposal

1. What goal will your website be designed to achieve?
    * Allow anyone interested in or already are keeping plants to find information on plants they want and help them keep track of those plants information.

2. What kind of users will visit your site? In other words, what is the demographic of your users?
    * Early College age to Adult.

3. What data do you plan on using? You may have not picked your actual API yet, which is fine, just outline what kind of data you would like it to contain.
    * Database from [permapeople.org](https://permapeople.org/knowledgebase/api-docs.html) Plant API. Information such as plant name and photo, plant description, watering requirements, hardiness etc.

4. In brief, outline your approach to creating your project (knowing that you may not know everything in advance and that these details might change later). Answer questions like the ones below, but feel free to add more information:
    * a. What does your database schema look like?
      * currently working on it.
    * b. What kinds of issues might you run into with your API?
      * Not having access to certain calls because there is a paid tier, properly associating plants from the API into the garden view
    * c. Is there any sensitive information you need to secure?
      * The users will be able to create an account so securing username and passwords with bcrypt will be a feature.
    * d. What functionality will your app include and what will the user flow look like?
      * The homepage will have a navbar at the top with 'create' and 'log in' or 'profile' and 'log out' and possibly a search bar for other users and gardens. A search bar in the body for plants and a prompt to create an account or log in if not logged in. Once logged in the homepage will show the same search bar with the 3 most recently created gardens underneath it.
      * An index page for a searched query displaying matches to that query.
      * Selecting a plant will show a view with information on it and options to add it to any created gardens and possibly favorite that plant for quicker access later.
      * The profile page will feature a profile picture, number of gardens created and cards for them below, and a create garden option. Possibly adding a feature to favorite certain plants and/or follow/friend other users.
    * f. What features make your site more than CRUD? Do you have any stretch goals?
      * Securely authinticating user accounts
