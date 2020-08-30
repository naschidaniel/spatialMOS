import axios from "axios";

export async function api(apiLink) {
  try {
    const response = await axios.get(apiLink);
    if (response.status == 200) {
      const data = await response.data;
      console.log(data)
      return data;
    } else {
      console.waring("The response status is " + response.status)
    }
  } catch (error) {
    console.error("The data for the Endpoint '" + apiLink + "' could not be loaded")
  }
}