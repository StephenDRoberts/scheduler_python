### Thoughts on code/best practices

* Where is it best to convert dates - during read_csv or in the formatters? My assumption is formatters.

### Assumptions

* A game can be processed by two collectors at the same time, one assessing the home team and another assessing the away
  team.


### Issues with the algorithm

* Tasks are ordered by processing deadline. However, I've not taken into account whether deferring the processing of a
  match to another shift would make it quicker.

