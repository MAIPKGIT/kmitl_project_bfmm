import { Component, NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ProductComponent } from './components/pages/product/product.component';
import { LoginComponent } from './components/pages/login/login.component';
import { AuthGuard } from './guard/auth.guard.guard';
import { OrderingComponent } from './components/ordering/ordering.component';
import { KitchenOrderComponent } from './components/pages/kitchen-order/kitchen-order.component';
import { TableStatusComponent } from './components/pages/table-status/table-status.component';
import { RecipeComponent } from './components/pages/recipe/recipe.component';
import { IngredientComponent } from './components/pages/ingredient/ingredient.component';
import { WasteComponent } from './components/pages/waste/waste.component';

const routes: Routes = [
  {path: "", component: LoginComponent},
  // {path: "ordering/:id", component: OrderingComponent, canActivate: [ AuthGuard ]},
  // {path: "ordering/:id", component: OrderingComponent},
  { path: "ordering/:id/:code", component: OrderingComponent },
  {path: "kitchen-order", component: KitchenOrderComponent},
  {path: "recipe/:id", component: RecipeComponent},
  {path: "table", component: TableStatusComponent, canActivate: [ AuthGuard ]},
  {path: "ingredient", component: IngredientComponent},
  {path: "waste", component: WasteComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
