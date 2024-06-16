import './App.css';
import { FormEvent, useEffect, useState } from 'react';
import axios from 'axios';
import { 
  ChakraProvider, Select, Input, Button, VStack, HStack, Box, Spinner, SimpleGrid, Center, Text
} from '@chakra-ui/react'
import { Product } from './components/Product';

function App() {
  const [apiValue, setApiValue] = useState([]);
  const [searchOptions, setSearchOptions] = useState({
    store: '',
    searchTerm: '',
    zipCode: '',
    city: '',
  });
  const [isSearching, setIsSearching] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [searchRun, setSearchRun] = useState(false);

  const handleSearch = async () => {
    setSearchRun(true);
    const { store, searchTerm, zipCode, city } = searchOptions;
    setErrorMessage('');
    setApiValue([]);
    setIsSearching(true);
    try {
      const requestUrl = encodeURI(`/prices/${store}?search_term=${searchTerm}&zip_code=${zipCode}&city_name=${city}`)
      const response = await axios.get(requestUrl);
      if (response.status === 200) {
        setApiValue(response.data);
      }
      setIsSearching(false);
    } catch (err) {
      console.error(err);
      setErrorMessage('There was a problem with getting the results.')
      setIsSearching(false);
    }
  }

  type SearchOptionTypes = 'store' | 'searchTerm' | 'zipCode' | 'city'

  const handleOptionChange = (e: FormEvent, optionName: SearchOptionTypes) => {
    const target = e.target as HTMLInputElement;
    const newOptions = { ...searchOptions };
    newOptions[optionName] = target.value;
    setSearchOptions({ ...newOptions });
  }

  return (
    <ChakraProvider>
      <Box>
        <HStack justify='center'>
          <Select 
            w='150px'
            placeholder='Select a store' 
            onChange={(e) => handleOptionChange(e, 'store')}
          >
            <option value={0}>Aldi</option>
            <option value={1}>Wegmans</option>
          </Select>
          <Input 
            w='200px'
            variant='outline'
            placeholder='Enter search term'
            onChange={(e) => handleOptionChange(e, 'searchTerm')}
          />
          <Input 
            w='200px'
            variant='outline' 
            placeholder='Enter zip code' 
            onChange={(e) => handleOptionChange(e, 'zipCode')}
          />
          <Input 
            w='200px'
            variant='outline'
            placeholder='Enter city name' 
            onChange={(e) => handleOptionChange(e, 'city')}
          />
          <Box w='50px'>
            <Button onClick={handleSearch}>Search</Button>
          </Box>
        </HStack>
        <Center>{ errorMessage !== '' ? <p>{errorMessage}</p> : null }</Center>
        { 
          isSearching ? 
          <HStack justify='center'>
            <p>Loading results</p>
            <Spinner />
          </HStack>
          :
          <Center>
            {
              apiValue.length > 0 ?
              <SimpleGrid minChildWidth='200px' spacing='30px' width='70%'>
                {
                  apiValue.map((item) => (
                    <Product 
                      key={`${item['name']},${item['price']}`}
                      name={item['name']}
                      price={item['price']}
                      quantity={item['quantity']}
                      isInStock={item['is_in_stock']}
                      imageUrl={item['image_url']}
                    />
                  ))
                }
              </SimpleGrid>
              :
              (
                searchRun && searchOptions.searchTerm.length > 0 ?
                <Text>{`There were no results for ${searchOptions.searchTerm}`}</Text>
                :
                null
              )
            }
          </Center>
        }
      </Box>
    </ChakraProvider>
  );
}

export default App;
